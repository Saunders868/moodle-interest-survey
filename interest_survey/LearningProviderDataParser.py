# NextcloudDownloader Script
#
# Description:
# This script parses the files in a download directory for the learning provider data files 
# and exports the data to a database, the parsed files are subsequently archived. The contents 
# of a log file are also exported at the end of the script. 
# 
# Version: 1.1.0
# Created: 23/08/2024
# Created By: Michael Andalcio
# Last Modified: 19/11/2024
# Last Modified By: Michael Andalcio

import configparser
import os
import sys
import logging
import pandas as pd
import shutil
from datetime import datetime
import sqlalchemy 
from sqlalchemy import create_engine
import re

# Global Configuration variables
CONFIG_LOG_FILE = os.environ.get('LOGFILE', '/WeLearnTT/scriptExecution.logs')
CONFIG_LOG_LEVEL = os.environ.get('LOGLEVEL', 'INFO')

class missingItemError(Exception):
    # Custom exception class for missing items in directories
    pass

class emptyVariableError(Exception):
    # Custom exception class for empty configuration variables
    pass

def configureLogging():    
    # Get numeric value for log level specified
    numeric_level = getattr(logging, CONFIG_LOG_LEVEL.upper(), None)

    # Create logging system with the specified parameters
    # Format - "Date Time":"Log Level":"Function Name":"Log description"
    logging.basicConfig(filename=CONFIG_LOG_FILE, 
                        level=numeric_level,
                        format= '"%(asctime)s";"%(levelname)s";"%(filename)s";"%(funcName)s";"%(message)s"',
                        datefmt="%Y-%m-%d %H:%M:%S")

def loadSettings():
    try:
        # Check if script Global Variables are set
        if not CONFIG_LOG_FILE:
            raise emptyVariableError("The CONFIG_LOG_FILE variable is blank")
        
        if not CONFIG_LOG_LEVEL:
            raise emptyVariableError("The CONFIG_LOG_LEVEL variable is blank")   
             
        # Create a dictionary with necessary parameters from configuration file
        config_values = {
            'download_directory': os.environ.get('LOCAL_DOWNLOAD', '/WeLearnTT/Downloads/'),
            'archive_directory': os.environ.get('LOCAL_ARCHIVE', '/WeLearnTT/Archive/'),
            'parsers': list((os.environ.get('PARSERS', 'Coursera Linux SimpliLearn Cisco')).split(' ')),
            'user': os.environ.get('DB_USER'),
            'password': os.environ.get('DB_PASS'),
            'host': os.environ.get('DB_HOST'),
            'port': os.environ.get('DB_PORT'),
            'database': os.environ.get('DB_NAME')
        }

        return config_values
    except emptyVariableError as e:
        logging.warning(e)
        exit()

    except missingItemError as e:
        logging.warning(e)
        exit()

    except Exception as e:
        logging.warning(e)
        exit()

def validateSettings(config):
    try:
        if checkFolderInDirectory(config['download_directory']):
            if len(os.listdir(config['download_directory'])) == 0:            # Check if there are no files in Download directory
                logging.warning("Download Directory is empty")
                return False  
            
            else:                                                   # If there are files in download directory
                if not os.path.isdir(config['archive_directory']):            # Check if archive directory exist
                    os.mkdir(config['archive_directory'])                     # If not create directory
                    logging.info('Created Archive Directory at: '+config['archive_directory'])
            
                selectedParser = sys.argv[1]

                if any(selectedParser in x for x in config['parsers']):
                    return True
                else:
                    logging.warning("Please enter value of valid parser.")
                
    except missingItemError as e:
        logging.warning(e)
        logging.warning("A valid path to a Download folder is required. Please update config file.")
        exit()

    except IndexError as e:
        logging.warning("Please enter an input argument")
    
def checkFileInDirectory(filePath):
    # Check if filepath variable specifies a file item
    if not os.path.isfile(filePath):
        raise missingItemError('The file does not exist at path: '+filePath)
    
    return True
    
def checkFolderInDirectory(folderPath):
    # Check if filepath variable specifies a folder item
    if not os.path.isdir(folderPath):
        raise missingItemError('The folder does not exist at path: '+folderPath)
    
    return True
    
def parserSwitch(config, selectedParser):
    successFlag = False
    logging.info(selectedParser+' parameter calling parser')

    # Calls learning provider parser for respective input argument
    if selectedParser == "Coursera":
        successFlag = parserCoursera(config)
    elif selectedParser == "Linux":
        successFlag = parserLinux(config)
    elif selectedParser == "SimpliLearn":
        successFlag = parserSimpliLearn(config)
    elif selectedParser == "Cisco":
        successFlag = parserCisco(config)

    if successFlag:
        logging.info('Executed '+selectedParser+' parser successfully')

def parserCoursera(config):
    try:
        courseraMembershipFile = removeTimestamp(config['download_directory'],'membership-report.csv')
        courseraUsageFile = removeTimestamp(config['download_directory'],'usage-report.csv')
        courseraSpecializationFile = removeTimestamp(config['download_directory'],'specialization-report.csv')
    
    except missingItemError as e:
        logging.error(e)
        logging.info("Please ensure all Coursera files are in the Downloads directory")
    
    else:
        parsedMembershipDataFrame = pd.read_csv(config['download_directory']+courseraMembershipFile)
        sqlExport(config, parsedMembershipDataFrame,"zMembershipData_Coursera","fail")

        parsedUsageDataFrame = pd.read_csv(config['download_directory']+courseraUsageFile)
        sqlExport(config, parsedUsageDataFrame,"zEnrolmentData_Coursera","fail")

        parsedSpecializationDataFrame = pd.read_csv(config['download_directory']+courseraSpecializationFile)
        sqlExport(config, parsedSpecializationDataFrame,"zSpecializationData_Coursera","fail")

        archiveFile(config['download_directory']+courseraMembershipFile, config['archive_directory'])
        archiveFile(config['download_directory']+courseraUsageFile, config['archive_directory'])
        archiveFile(config['download_directory']+courseraSpecializationFile, config['archive_directory'])
        return True

def parserLinux(config):
    try:
        linuxFile = removeTimestamp(config['download_directory'],'eLearning Client Usage.xlsx')
    
    except missingItemError as e:
        logging.error(e)
        logging.info("Please ensure the eLearning Client Usage file is in the Downloads directory")
    
    else:
        parsedDataFrame = pd.read_excel(config['download_directory']+linuxFile)
        sqlExport(config, parsedDataFrame,"zEnrolmentData_Linux","fail")

        archiveFile(config['download_directory']+linuxFile, config['archive_directory'])
        return True

def parserSimpliLearn(config):
    try:
        simplilearnFile = removeTimestamp(config['download_directory'],'The_Commonwealth_Learner_Activity.csv')
    
    except missingItemError as e:
        logging.error(e)
        logging.info("Please ensure the SimpliLearn file is in the Downloads directory")
    
    else:
        parsedDataFrame = pd.read_csv(config['download_directory']+simplilearnFile)

        fileColumns = ['Learner Name','Learner Email','Account Status','Order Type','Team','Last Login Date','Last Activity On','Self-Learning Time','Course Assignment Date','Course Activation Date','Course Expiration Date','Course Access','Course Type','Course Id','Course Name','Self-Learning Completion %','Certificate Unlock Date','Activity Level','Learning days','Program Id','Enrolment Cohort ID','Enrolment Cohort Name','Current Cohort ID','Current Cohort Name','Current Cohort Start Date','Current Cohort End Date','Cohort Enrollment Date','Classes Completed/Overall Classes','Mentoring Registered', 'Mentoring Attended', 'Live Classes Registered', 'Live Sessions Attended']

        parsedDataFrame1 = parsedDataFrame[fileColumns]

        parsedDataFrame = parsedDataFrame.rename(columns={'Classes Completed/Overall Classes':'Overall Classes'})


        columnNames = {"Assessment Test": [3], "Project Name": [4], "Class": [4]}

        parsedAssessmentDataFrame = pd.DataFrame()
        parsedProjectDataFrame = pd.DataFrame()
        parsedClassDataFrame = pd.DataFrame()

        for series_name, series in parsedDataFrame.items():

            if any(series_name.startswith(x) for x in columnNames.keys()):

                columnStart = parsedDataFrame.columns.get_loc(series_name)

                columnEnd = columnStart+columnNames[series_name.rsplit(' ',1)[0]][0]

                range1 = [num for num in range(columnStart, columnEnd)]
                range1.append(parsedDataFrame.columns.get_loc('Learner Email'))
                range1.append(parsedDataFrame.columns.get_loc('Course Name'))

                temp = parsedDataFrame.iloc[:, range1]

                temp =  temp[temp.iloc[:, 0].notna()]

                if "Assessment Test" == series_name.rsplit(' ',1)[0]:
                    temp.columns = ["Assessment Test","Best Score","Attempt Date","Learner Email","Course Name"]
                    parsedAssessmentDataFrame = pd.concat([parsedAssessmentDataFrame, temp], ignore_index=True)

                elif "Project Name" == series_name.rsplit(' ',1)[0]:
                    temp.columns = ["Project Name","Project Result","Attempts Count","Submit Date","Learner Email","Course Name"]
                    parsedProjectDataFrame = pd.concat([parsedProjectDataFrame, temp], ignore_index=True)

                elif "Class" == series_name.rsplit(' ',1)[0]:
                    temp.columns = ["Class","% of Sessions attended","Session completed count in Class","Average Time Spent Per Session in Class","Learner Email","Course Name"]
                    parsedClassDataFrame = pd.concat([parsedClassDataFrame, temp], ignore_index=True)

        sqlExport(config, parsedDataFrame1,"zEnrolmentData_SimpliLearn","fail")
        sqlExport(config, parsedAssessmentDataFrame,"zAssessmentData_SimpliLearn","fail")
        sqlExport(config, parsedProjectDataFrame,"zProjectData_SimpliLearn","fail")
        sqlExport(config, parsedClassDataFrame,"zClassData_SimpliLearn","fail")

        archiveFile(config['download_directory']+simplilearnFile, config['archive_directory'])
        return True

def parserCisco(config):
    try:
        checkFolderInDirectory(config['download_directory']+'Cisco Data/')

        ciscoFolderPath = config['download_directory']+'Cisco Data/'        #Absolute path to directory with CISCO files
        ciscoFiles = os.listdir(ciscoFolderPath)                                #Get list of all files and folders in directory
    
    except missingItemError as e:
        logging.error(e)
        logging.info("Please ensure the Cisco Data folder is in the Downloads directory")
    
    else:
        parsedDataFrame = pd.DataFrame()

        for file in ciscoFiles:
            try:
                parsedFileDataFrame = pd.read_csv(ciscoFolderPath+file)
                dfColumns = ['NAME','EMAIL','INVITATION DATE','STATUS','ENROLLMENT DATE']

                parsedFileDataFrame.columns =  dfColumns

                fileName, fileExtension = os.path.splitext(file)
                
                course = fileName[:-16]

                parsedFileDataFrame.insert(0, "courses", course)                                           #Add course to dataframe

                parsedDataFrame = pd.concat([parsedDataFrame, parsedFileDataFrame], ignore_index=True)                 #Appends file dataframe to learning provider dataframe
            
            except ValueError as e:
                logging.warning(file+"does not match format")
                
        sqlExport(config, parsedDataFrame,"zEnrolmentData_Cisco","fail")

        archiveFile(config['download_directory']+'Cisco Data/', config['archive_directory'])
        return True

def removeTimestamp(directory, desiredFile):
    fileName, fileExtension = os.path.splitext(desiredFile)
    
    # Prepare regex pattern to match files with timestamp
    pattern = re.compile(rf"{re.escape(fileName)}.*_\d{{8}}:\d{{6}}{re.escape(fileExtension)}")
    
    for itemName in sorted(os.listdir(directory)):
        if pattern.match(itemName):
            return itemName
        
    raise missingItemError('The file does not exist in download directory: '+desiredFile)

def archiveFile (fileABSPath, archiveDirectory):
    currentDate =  (datetime.now()).strftime('%Y%m%d')          #Store current date in YYYYMMDD format

    if not os.path.isdir(archiveDirectory+currentDate+"/"):    #If archive does not have a directory for current date
            os.mkdir(archiveDirectory+currentDate+"/")         #Create directory
            logging.info('Created Archive Directory for '+currentDate+' at : '+archiveDirectory+currentDate)

    shutil.move(fileABSPath,archiveDirectory+currentDate+"/")  #Move file to archive for current date
    logging.info('Archived '+fileABSPath+' to '+archiveDirectory+currentDate+'/ directory successfully')
    
def sqlExport (config, parsedDataFrame, exportTable, condition):
    try:
        # Create a SQLAlchemy engine
        connection_string = f"mysql+pymysql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
        engine = create_engine(connection_string)
        
        # Write DataFrame to SQL table
        parsedDataFrame.to_sql(exportTable, con=engine, if_exists=condition, index=False)

        logging.info('Export data to '+exportTable+' table successfully')
        
        return True
    except Exception as e:
        logging.error(e)
        logging.error("An error occured while connecting/pushing data to "+config['host']+" database")

def logExport (config):
    parsedLogFile = pd.read_csv(CONFIG_LOG_FILE, sep=";", header=None)
    parsedLogFile.columns =  ["logDateTime","severity","source","function","description"]

    if sqlExport(config, parsedLogFile, "ExecutionLogs", "append"):
        os.remove(CONFIG_LOG_FILE)

    logging.info('Logs exported successfully') 

def main():
    configureLogging()
    logging.info('Executing LearnerProviderDataParser')

    config = loadSettings()
    if validateSettings(config):
        parserSwitch(config, sys.argv[1])

    logExport(config)

if __name__=="__main__":
    main()