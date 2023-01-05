import geopandas as gpd
import rasterio
import pandas as pd
import rasterio
from rasterio.mask import mask


def extract_dataframe_pixels_values_from_tif_and_polygons(path_to_tif, path_to_polygons):
        """
        This method extracts pixels from annotated polygons and puts then in a pandas dataframe.
        In order to be used in a model. 

        @param path_to_tif: The raster file of a satellite image from which the pixel values have to extracted.
        @param  path_to_polygons: the path to the annotations in polygons which will  be used to crop the image for pixels with
        @return a pandas dataframe which pixel values for annotations.
        """
        geo_file = gpd.read_file(path_to_polygons)
        src = rasterio.open(path_to_tif)
        df = pd.DataFrame([])
        
        print('raster path opened')
        print('convert to RD')
        for index, row in geo_file.iterrows():
                
                # Change the crs to rijks driehoek, because all the satelliet images are in rijks driehoek
                if geo_file.crs != 'epsg:28992':
                        geo_file = geo_file.to_crs(epsg=28992)

                out_image, out_transform = mask(src,row['geometry'], crop=True)
                out_meta = src.profile.copy()

                out_meta.update({
                                "height": out_image.shape[1],
                                "width": out_image.shape[2],
                                "transform": out_transform})
               
                df_row = pd.DataFrame([ band.flatten()  for band in out_image]).transpose()
                df_row.columns = ["r","g","b","i","ndvi","height"]
                df_row['label'] = row["label"]
                df_row['image'] = path_to_tif.split("/")[-1]
                df = df.append(df_row)
        
        src.close()
        df = df[df['r'] !=0].reset_index().drop(['index'],axis=1)
        return df