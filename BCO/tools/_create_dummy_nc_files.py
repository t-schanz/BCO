from netCDF4 import Dataset


nc = Dataset("dummy_nc_file_netcdf4.nc",mode="w",data_model="NETCDF4_CLASSIC")
nc.close()