from app.models.pathfotos import CreatePathFoto
from app.models.estadisticas import CreateStatistics
from app.GeoShit.NASA_winner import *
from app.GeoShit.rgb_example import *

def Sentinel( data, name, zone, geom ):
    file_json = 'TestJS-9381bfacfaba.json'
    bucket_name = 'docas'

    predio = 10014
    now    = datetime.now()
    delta  = timedelta( weeks = 6 )
    date_time = now.strftime("%Y-%m-%d")
    past_time = (now-delta).strftime("%Y-%m-%d")

    dates, ndvi_data, parameters = modis_ndvi_time( geom )
    ndvi_data = np.mean( ndvi_data, axis=(0,1) )

    np.save( name ,ndvi_data )
    numpy_save = np.load( name + ".npy" )

    ndvi, now_date, coords, geotrasform, stats = ndvi_sentinel_calculation( geom, past_time, date_time )
    colormap_image( name+"NDIV" , ndvi )

    client = storage.Client.from_service_account_json( file_json )
    bucket = client.get_bucket(bucket_name)
    url_ndvi = upload_ndvi( name+"NDIV" , bucket )

    rgb_data, now_date, coords, parameters = rgb_sentinel( geom, past_time, date_time )
    colormap_rgb( name+"RGB", rgb_data )
    client = storage.Client.from_service_account_json( file_json )
    bucket = client.get_bucket(bucket_name)
    url_rgb = upload_ndvi( name+"RGB" , bucket )

    new_foto_id = CreatePathFoto( url_ndvi, url_rgb, coords[0][0], coords[0][1], coords[1][0], coords[1][1], zone.id )
    CreateStatistics(stats['area_0.00'],stats['area_0.25'],stats['area_0.50'],stats['area_0.75'],stats['area_1.00'],stats['p_0.05'],stats['p_0.25'],stats['p_0.50'],stats['p_0.75'],stats['p_0.95'],stats['mean'],stats['std'],stats['mean/pixel'],new_foto.id)
