"""
awot.io.read_latmos_falcon_flight
=========================

This is a grouping of scripts designed to process LATMOS 
 Falcon-F20 flight level data recorded during flights 
 and NASA Ames Ascii format
"""
# Load the needed packages
import nappy
from netCDF4 import Dataset, num2date, date2num
from datetime import datetime
import numpy as np
import pytz

def flight_data(fname, mapping_dict=None):
    """
    Read in data from NASA Ames formatted ASCII file containing
    LATMOS Falcon-F20 aircraft flight level data

    Parameters
    ----------
        fname : string
            Filename [string]
        mapping_dict : dict
            Mapping dictionary to use for pulling data in
            If None, uses default dictionary.

    Output
    ------
        data : Dictionary of the following values
            Lat : float
                Aircraft latitude [deg]
            Lon : float
                Aircraft longitude [deg]
            Alt : float
                Aircraft altitude [m]
                
            PAlt : float
                Aircraft pressure altitude [m]
            Time : float
                Aircraft time array
            heading : float
                Aircraft true heading [deg]
            track : float
                Aircraft track [deg]
            vert_vel_DPJ : float
                Vertical wind via D Jorgensen calculation [m/s]
            temp : float
                Ambient Temperature [C]
            temp_dew : float
                Dewpoint Temperature [C]
            temp_virt : float
                Virtual Temperature [K]
            theta : float
                Potential Temperature [K]
            thetaE : float
                Equivalent Potential Temperature [K]
            thetaV : float
                Virtual Potential Temperature [K]
            wSpd : float
                Wind Speed [m/s]
            wDir : float
                Wind Direction [deg]
            RH : float
                Relative Humidity [%]
            SH : float
                Specific Humidity [g/kg]
            mixing_ratio : float
                Mixing ratio [g] [g/g?]
            vap_press : float
                Vapor Pressure [hPa]
            sat_vap_press : float
                Saturated Vapor Pressure [hPa]
            project : str
                Project name
            platform : str
                Platform name
            flightnum : str
                Flight number
       
    USAGE::
     data = flight_track(fname)
    """
    # Read the file
    FileIn = nappy.openNAFile(fname)

    # Make sure this is really a UND Citation file, always 1001
    if FileIn.getFFI() != 1001:
        print "Check if this is a UND Citation file!"
        FilenIn.close()
        return

    # Get the whole file as a dictionary (NA = NASA Ames)
    NA_dict = FileIn.getNADict()

    # Pull out global attributes
    project = NA_dict['MNAME']
    platform = NA_dict['SNAME']
    comments = NA_dict['NCOM']
    missingData = NA_dict['VMISS']
    scaleFactor = NA_dict['VSCAL']
    hdr_row_length = NA_dict['NLHEAD']
    flight_number = comments[1].split(':')

    # Now add a value to beginning of missing data scale factor arrays
    # to account for time column
    missingData.insert(0, missingData[-1])
    scaleFactor.insert(0, scaleFactor[-1])

    # Get the data columns
    junk = np.genfromtxt(fname, skiprows=hdr_row_length, 
                          missing_values=missingData, filling_values=np.nan)

    # Get the variable names
    # Need to split on ":" and then remove white space
#    VarNames = [varlong.split(':')[0].replace(" ", "") for varlong in NA_dict['VNAME']]
    VarNames = NA_dict['VNAME']
    # Insert the Time variable that is the first column
    VarNames.insert(0, 'time')

    # Pull out each variable data and multiply by scale factor
    # The altitude is currently the INS altitude measurement,
    # there is a 2nd GPS mx as well
    # The humidity mx is from Aerodata sensor, 2nd mx from hygrometer

    # Grab a name map for falcon data
    if mapping_dict is None:
        name_map = _get_name_map()
    else:
        name_map = mapping_dict

    # Loop through the variables and pull data
    readfile = {}
    for jj, name in enumerate(VarNames):
        readfile[name] = np.array(junk[:, jj] * scaleFactor[jj])
        readfile[name] = np.ma.masked_values(readfile[name], missingData[jj])

    # Now work out the time into a datetime instance
    # Get the date
    Date = NA_dict['DATE']
    DateStr = str(Date[0])+'-'+str(Date[1])+'-'+str(Date[2])

#    TimeSec = readfile['time'][:]
#    time_units_string = 'seconds since '+DateStr+' 00:00:00+0:00'
#    # Create a datetime instance from file
#    Time_dt = num2date(TimeSec, units=time_units_string)
#    # Now move this back into number format
#    TimeNum = date2num(Time_dt, units='seconds since 1970-1-1 00:00:00+0:00')

    StartTime = datetime(Date[0], Date[1], Date[2], 0, 0, 0)
    TimeSec = np.array(readfile['time'][:]) + date2num(StartTime, units='seconds since 1970-1-1 00:00:00+0:00')

    # Finally convert this back to a standard used by this package (Epoch)
    Time_unaware = num2date(TimeSec[:], units='seconds since 1970-1-1 00:00:00+0:00')
    Time = Time_unaware#.replace(tzinfo=pytz.UTC)

    del readfile['time']
    readfile['time'] = Time

    data = {}
    for varname in name_map:
        try:
            data[varname] = readfile[name_map[varname]]
        except:
            data[varname] = None

    # Add some values to the data dictionary
    data['project'] = project
    data['platform'] = platform
    data['flight_number'] = flight_number

    FileIn.close()
    return data 

def _get_name_map(mapping=None):
    '''Map out names used in Falcon data to AWOT'''
    name_map = {
               'time': 'time',
               'latitude': 'latitude : from GPS (degree)',
               'longitude': 'longitude : from GPS (degree)',
               'altitude': 'altitude : from GPS (meter)',
               'true_heading': 'platform_orientation : from INS (degree)',               
               'temperature': 'air_temperature : from deiced Rosemount sensor (Celsius)',               
               'dewpoint_temperature': 'dew_point_temperature : from 1011B top dew-point hygrometer (Celsius)',               
               'wind_spd': 'wind_speed : Attitudes and speed wrt ground from INS, air angles from radome, air speed from pitot (m/s)',
               'wind_dir': 'wind_from_direction : Attitudes and speed wrt ground from INS, air angles from radome, air speed from pitot (degree)',
               'relative_humidity': 'relative_humidity : from Aerodata sensor (%)',
               'mixing_ratio': 'humidity_mixing_ratio : from Aerodata sensor (gram/kg)',
               'pressure': 'air_pressure : from front sensor, corrected for the so-called static defect (hPa)',
               'roll': 'platform_roll_angle : from INS (degree)',
               'pitch': 'platform_pitch_angle : from INS (degree)',
               'aircraft_air_speed': 'platform_speed_wrt_air : from pitot (m/s)',
               'platform_ground_speed': 'platform_speed_wrt_ground : from GPS (m/s)',
               'platform_ground_speed2': 'platform_speed_wrt_ground : from INS (kt)',
               'aircraft_vert_accel': 'platform_acceleration_along_vertical_axis : from INS (meter second-2)',
               'altitude2': 'altitude : from INS (meter)',
               'mixing_ratio2': 'humidity_mixing_ratio : from top dew-point hygrometer (GE 1011B) (gram/kg)',
               'platform_course': 'platform_course : from INS (degree)',
               'platform_upward_ground_speed': 'upward_platform_speed_wrt_ground : from INS (m/s)',
               'platform_upward_ground_speed': 'upward_platform_speed_wrt_ground : from GPS (m/s)',
               'attack_angle': 'angle_of_attack : from sensor on the boom (degree)',
               'sideslip_angle': 'angle_of_sideslip : from sensor on the boom (degree)',
               'Uwind': 'eastward_wind : Attitudes and speed wrt ground from INS, air angles from radome, air speed from pitot (m/s)',
               'Vwind': 'northward_wind : Attitudes and speed wrt ground from INS, air angles from radome, air speed from pitot (m/s)',
               'air_vertical_velocity': 'upward_air_velocity : Attitudes and speed wrt ground from INS, air angles from radome, air speed from pitot (m/s)',
               'wind_dir2': 'wind_from_direction : Attitudes and speed wrt ground from INS, air angles from radome, air speed from pitot (degree)',
               'wind_spd2': 'wind_speed : Attitudes and speed wrt ground from INS, air angles from radome, air speed from pitot (m/s)',
               }
    return name_map