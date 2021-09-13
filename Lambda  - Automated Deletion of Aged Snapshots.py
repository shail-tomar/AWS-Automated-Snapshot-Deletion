#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import json  
import boto3                #   Amazon SDK
import pandas as pd         #   Formatting of excel file and performing operation on excel
import io                   #   Handling Input/Output
from io import BytesIO 
import botocore             #   ErrorHandling
import xlsxwriter           #   Writing to Excel
import awswrangler          #   Importing Openpyxl and performing complex read operations on it 
import datetime 
key = 'Account Details for Volume Conversion.xlsx'                 # ^^^^INPUT FOLDER NAME/INPUT DOCUMENT NAME
bucket = 'nishubuckettest'                                         # ^^^^BUCKET NAME
                    
s3=boto3.client('s3')   
file_object =s3.get_object(Bucket=bucket, Key=key)
file_content = file_object['Body'].read()
b_file_content = io.BytesIO(file_content)                                
df= pd.read_excel(b_file_content)                                                     # df = dataframe for pandas
df_sheet_index = pd.read_excel(b_file_content, sheet_name=0)                          # first sheet from excel is read
h_column_list_of_excel_file = df_sheet_index.columns.ravel().tolist()
b_file_content.close()    

acc_id=[]
acc_name=[]
account_id = []
name_missing_list = []
Comments = []
Reason_for_error = []
account_ID = []
Flag_for_name = False
Flag_for_ec2_permission_role_error = True 
acc_id_causing_error = []
acc_name_causing_error =[]
serial_number_for_comments_sheet = []
serial_number_for_comments = 0
Flag_for_id = False  
id_missing_list = [] 
accId=[] 
accName = [] 
accid_from_excel=df_sheet_index[h_column_list_of_excel_file[1]].tolist()
accName_from_excel=df_sheet_index[h_column_list_of_excel_file[2]].tolist() 
print(accid_from_excel) 
for i in range(len(accid_from_excel)):
    if pd.isnull(accid_from_excel[i]) == False :    
        accId.append(int(accid_from_excel[i])) 
        accName.append(accName_from_excel[i])
    else: 
        id_missing_list.append(i+1)
        Flag_for_id = True 
        Reason_for_error.append("Account Id Missing") 
        Comments.append("Account Id Missing at {}".format(i+1))
        acc_name_causing_error.append(accName_from_excel[i]) 
        acc_id_causing_error.append("")
        serial_number_for_comments = serial_number_for_comments + 1 
        serial_number_for_comments_sheet.append(serial_number_for_comments) 
    
print(accId)

for each in range(len(accName)):                 # for finding the missing entries in acc name and account id in the input excel
    if pd.isnull(accName[each])== False :   
        account_ID.append(accId[each])
        acc_name.append(accName[each]) 
    else:
        name_missing_list.append(i+1)
        Flag_for_name = True 
        Reason_for_error.append("Account Name Missing") 
        Comments.append("Account Name Missing at {}".format(each+1))
        acc_name_causing_error.append("")  
        acc_id_causing_error.append(accId[each])  
        serial_number_for_comments = serial_number_for_comments + 1 
        serial_number_for_comments_sheet.append(serial_number_for_comments) 
print(account_ID)         
for each in account_ID:
    account_id.append(str(each))
print(account_id) 

client = boto3.client('sts')
master_acc_id = client.get_caller_identity()['Account']
print(master_acc_id) 

for each in account_id:
    if len(each)==12:
        acc_id.append(each)
    else :
        N=12-len(each)
        each = each.rjust(N + len(each), '0')
        acc_id.append(each)  
  
rolearn = []  
for each in range(len(acc_id)):
    if acc_id[each] != master_acc_id:
        rolearn.append("arn:aws:iam::{}:role/Cross_Account_Role".format(acc_id[each]))   # ^^^ROLE NAME
dict_for_name = dict(zip(acc_id,acc_name))        
print(rolearn)
Flag_for_role_error = False
Flag_for_ec2_permission_role_error = False

#--------------------Conversion work Report---------------------------------------------------------------------------

def aged_snapshot_deletion(): 
    serial_number_for_comments_new = serial_number_for_comments
    serial_number = 0
    serial_number_stored_in_xlsx = [] 
    acc_id_stored_in_xlsx = []
    acc_name_stored_in_xlsx = []  
    VolumeId_stored_in_xlsx = []  
    volume_with_status = []
    description = []
    Region_stored_in_xlsx = []
    snapshot_id_stored_in_xlsx = []
    size_stored_in_xlsx = []
    status_stored_in_xlsx = []
    for each in range(len(rolearn)): 
        try:                 
            sts_connection = boto3.client('sts')                                #temporary credentials 
            acct_b = sts_connection.assume_role(
            RoleArn=rolearn[each],     
            RoleSessionName="Cross_Account_Role"                               # ^^^^ROLE NAME
            )   
            
            ACCESS_KEY = acct_b['Credentials']['AccessKeyId']
            SECRET_KEY = acct_b['Credentials']['SecretAccessKey']    
            SESSION_TOKEN = acct_b['Credentials']['SessionToken']
    
            client = boto3.client('ec2',
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
            aws_session_token=SESSION_TOKEN,
                )
                
            ACC_ID = rolearn[each].split(":")[4]
            ec2_regions = [region['RegionName'] for region in client.describe_regions()['Regions']]
            
            try:
                
                for region in ec2_regions:  
#                     if region == 'ap-south-1':
                    client = boto3.client('ec2',region,
                    aws_access_key_id=ACCESS_KEY,
                    aws_secret_access_key=SECRET_KEY,
                    aws_session_token=SESSION_TOKEN,
                        )
                    ec2 = boto3.resource('ec2',region,
                    aws_access_key_id=ACCESS_KEY,
                    aws_secret_access_key=SECRET_KEY,
                    aws_session_token=SESSION_TOKEN,
                    )
                    # snapshots having the tags as 'Team :Devops'
                    snapshots = client.describe_snapshots(Filters=[{'Name': 'tag:Team', 'Values': ['Devops']}])
                    print(snapshots)    
                    for snapshot in snapshots['Snapshots']:
                        start_time=snapshot['StartTime']              #finding the date of creation of snapshot
                        date=start_time.date()
                        today_date=datetime.datetime.now().date()    #today's date
                        difference_of_days=today_date-date   

                        try:
                            if difference_of_days.days>30 :          #deleting 30 days snapshot
                                id = snapshot['SnapshotId']
                                print(id) 
                                # client.delete_snapshot(SnapshotId=id) #uncomment the given line to delete
                        except botocore.exceptions.ClientError as e:
                            if 'InvalidSnapshot.InUse' in e.message:
                                print("skipping this snapshot")
                                continue
                        serial_number = serial_number + 1
                        serial_number_stored_in_xlsx.append(serial_number)
                        acc_id_stored_in_xlsx.append(ACC_ID)
                        for ac_id,name in dict_for_name.items(): 
                            if ac_id == ACC_ID: 
                                acc_name_stored_in_xlsx.append(name)
                        Region_stored_in_xlsx.append(region)
                        VolumeId_stored_in_xlsx.append(snapshot['VolumeId']) 
                        # volume_with_status.append(volume.volume_type) 
                        description.append(snapshot['Description'])

                        snapshot_id_stored_in_xlsx.append(snapshot['SnapshotId'])  
                        size_stored_in_xlsx.append(snapshot['VolumeSize'])
                        status_stored_in_xlsx.append(snapshot['State']) 

            except botocore.exceptions.ClientError as error:
                Flag_for_ec2_permission_role_error = True
                Comments.append(error)
                serial_number_for_comments_new = serial_number_for_comments_new + 1
                serial_number_for_comments_sheet.append(serial_number_for_comments_new)  
                Reason_for_error.append("EC2/EBS Permission Related")
                ACC_ID = rolearn[each].split(":")[4] 
                acc_id_causing_error.append(ACC_ID)
                for ac_id,name in dict_for_name.items(): 
                    if ac_id == ACC_ID: 
                        acc_name_causing_error.append(name) 
                
        except botocore.exceptions.ClientError as error:
            Flag_for_role_error = True
            # print(error) 
            Comments.append(error)
            Reason_for_error.append("Assume Role Issue")
            serial_number_for_comments_new = serial_number_for_comments_new + 1
            serial_number_for_comments_sheet.append(serial_number_for_comments_new)
            ACC_ID = rolearn[each].split(":")[4]
            acc_id_causing_error.append(ACC_ID)
            for ac_id,name in dict_for_name.items(): 
                if ac_id == ACC_ID: 
                    acc_name_causing_error.append(name)  
            
                                                 # for master account
    for i in range(len(acc_id)):
        if acc_id[i]==master_acc_id:
            client = boto3.client('ec2')   
            try:
                ec2_regions = [region['RegionName'] for region in client.describe_regions()['Regions']]
                for region in ec2_regions:    
#                     if region == 'ap-south-1':
                    client = boto3.client('ec2',region)
                    #filtering based on tags
                    snapshots = client.describe_snapshots(Filters=[{'Name': 'tag:Team', 'Values': ['Devops']}])
                    print(snapshots)
                    for snapshot in snapshots['Snapshots']:

                        start_time=snapshot['StartTime']          #date of creation of snapshot
                        date=start_time.date()
                        today_date=datetime.datetime.now().date()  #today's date
                        difference_of_days=today_date-date   

                        try:
                            if difference_of_days.days>30 :
                                id = snapshot['SnapshotId']
                                print(id) 
                                # client.delete_snapshot(SnapshotId=id)   #uncomment the given line for deleting
                        except botocore.exceptions.ClientError as e:
                            if 'InvalidSnapshot.InUse' in e.message:
                                print("skipping this snapshot")
                                continue

                        serial_number = serial_number + 1
                        serial_number_stored_in_xlsx.append(serial_number)
                        acc_id_stored_in_xlsx.append(acc_id[i])
                        acc_name_stored_in_xlsx.append(acc_name[i])
                        Region_stored_in_xlsx.append(region)
                        VolumeId_stored_in_xlsx.append(snapshot['VolumeId'])
                        # volume_with_status.append(volume.volume_type) 
                        description.append(snapshot['Description'])
                        snapshot_id_stored_in_xlsx.append(snapshot['SnapshotId'])  
                        size_stored_in_xlsx.append(snapshot['VolumeSize'])
                        status_stored_in_xlsx.append(snapshot['State']) 
            except botocore.exceptions.ClientError as error:
                Flag_for_ec2_permission_role_error = True
                Comments.append(error)
                serial_number_for_comments_new = serial_number_for_comments_new + 1
                serial_number_for_comments_sheet.append(serial_number_for_comments_new)  
                Reason_for_error.append("EC2/EBS Related")
                acc_id_causing_error.append(acc_id[i])
                acc_name_causing_error.append(acc_name[i]) 
    
    # print(Comments)
    # print(len(serial_number_stored_in_xlsx))
    # print(len(acc_id_stored_in_xlsx))
    # print(len(acc_name_stored_in_xlsx))
    # print(len(VolumeId_stored_in_xlsx))
    # print(len(Region_stored_in_xlsx))
    # # print(len(volume_with_status))
    # # print(len(description))
    # print(len(size_stored_in_xlsx))
    
    #excel storage work
    data={'S No ':serial_number_stored_in_xlsx, 'Account Id':acc_id_stored_in_xlsx, 'Account Name':acc_name_stored_in_xlsx,'Region':Region_stored_in_xlsx,'Volume Id': VolumeId_stored_in_xlsx,'Snapshot Id': snapshot_id_stored_in_xlsx,'Description':description,'State':status_stored_in_xlsx, 'Size': size_stored_in_xlsx}
    data_frame=pd.DataFrame(data)
    
    data_for_error={'S.No':serial_number_for_comments_sheet, 'Account Id':acc_id_causing_error,'Account Name':acc_name_causing_error,'Possible Cause ':Reason_for_error, 'Comments':Comments}
    data_frame_error=pd.DataFrame(data_for_error)
    
    io_buffer = io.BytesIO()   
    s3 = boto3.resource('s3')  
    writer = pd.ExcelWriter(io_buffer, engine='xlsxwriter')
    sheets_in_writer=['Snapshot Details','Comments']
    data_frame_for_writer=[data_frame, data_frame_error]
    for i,j in zip(data_frame_for_writer,sheets_in_writer):
        i.to_excel(writer,j,index=False)    
    workbook=writer.book
    header_format = workbook.add_format({'bold': True,'text_wrap': True,'size':12, 'font_color':'black','valign': 'center','fg_color':'9ACD32','border': 1})
    max_col=4   
    header_format_comments = workbook.add_format({'bold': True,'text_wrap': True,'size':12, 'font_color':'black','valign': 'center','fg_color':'F2FBA1','border': 1}) 
    
    
    worksheet=writer.sheets["Snapshot Details"]   
    
    for col_num, value in enumerate(data_frame.columns.values): 
        worksheet.write(0, col_num, value, header_format) 
        worksheet.set_column(1, 7, 20)
        worksheet.set_column(4,4,40) 
        
        
        
    worksheet=writer.sheets["Comments"]  
    
    for col_num, value in enumerate(data_frame_error.columns.values): 
        worksheet.write(0, col_num, value, header_format_comments)  
        worksheet.set_column(0,2,15)  
        worksheet.set_column(3,3,25)  
        worksheet.set_column(4,4,45)   
        
    filepath = 'Aged Snapshot Report.xlsx'                               #document name
    writer.save()     
    data = io_buffer.getvalue() 
    s3.Bucket('nishubuckettest').put_object(Key=filepath, Body=data)         #specify the bucket name
    io_buffer.close()   
    aged_snapshot_deletion.has_been_called = True 
    
def lambda_handler(event, context):
    
    aged_snapshot_deletion.has_been_called = False
    
    aged_snapshot_deletion()    #function called to perform deletion work
    
    if aged_snapshot_deletion.has_been_called:
        return "Snapshot Deleted"
    else:
        return "No operation done"               

