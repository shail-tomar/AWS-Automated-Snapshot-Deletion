# AWS-Automated-Snapshot-Deletion
# Functionality
This automation script will deletion old snapshots across all regions and in multiple accounts based on Tags based on the number of configured days.

* An AWS Account Access with necessary permissions.
* A Lambda where we can execute Script with necessary permissions.
      -----Permissions
		a) S3 Full Access
		b) EC2 Full Access
		b) Change the execution time to more than 3 min.
		c) Trust Relation built between child accounts and parent account using IAM Roles.
                   Use this link for creating the IAM Roles: https://louay-workshops.com.au/iam-deep-dive/04_cross-account/lambdacrossaccounts3.html
* A csv file with 3 columns names as "S.No, AccountId, AccountName". Please ensure that the information entered in AccountId Column is formatted to numbers with 0 decimals(Using Format Cells Feature).
* Name this csv file created as "Account Details for snapshot work" or anything as needed.

--->for CHILD ACCOUNT
			a) Create Role--> Another AWS Account(Parent Account Id) -->Policy--> S3FullAccess and EC2FullAccess and then name it. Save the Role name. Put this Role name in Policy of Parent Account.	
                        b) Create this role with the same name for all the child accounts.

--->for PARENT ACCOUNT
			a) Create Policy --> Add STS
					 --> Choose Action as Write--> Assume Role
					 --> Choose Resources --> Specific
							      --> Add Arn as "arn:aws:iam::*:role/ROLE NAME created in Child Accounts"

	

* Do the required changes in the lambda for 
				a)Bucket Name
				b)Role Name(this is the role name created in child accounts using steps mentioned above for IAM creation)
				c)Folders Name
				d)Document name
                                e)Provide S3FullAccess and EC2FullAccess to the lambda created in parent account as we will be reading from S3 and saving the information in it.
				f)Attach the policy created earlier for Parent account.(MUST)
				g)Add the Tags as needed ...for example: "Team:Devops"	


###OUTPUT

1. This Script will list down all the snapshots created 'x' days earlier across multiple regions and multiple accounts.

2. Deletes the old snapshots.


