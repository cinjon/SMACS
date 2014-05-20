import re

date_regex  = re.compile("^(\d{1,2})/(\d{1,2})/(\d{4})$")
dose_regex = re.compile("^(.*)\s(\d*\.*\d+)\s{0,1}([a-z\%]+)|(.*)\s(\d*\.*\d+[a-z\%]*\-\d*\.*\d+\s{0,1}[a-z\%]*)$")
price_regex = re.compile("^([\d*O*\d*]+)[^\d]+([\d*O*]{4,5})\?*$") #so not robust, ugh.
parens_regex = re.compile("^\(1([\d*0*]{5})$") #sometimes, 0 looks like (1 to ghostscript

master_list_date_regex = re.compile("^illinois_master_smac_([a-z]+)_(\d{1,2})_(\d{4}).pdf$")
master_specialty_list_date_regex = re.compile("^illinois_master_specialty_smac_([a-z]+)_(\d{1,2})_(\d{4}).pdf$")
prop_list_date_regex = re.compile("^proposed-smac-list-effective-(\d+)-(\d+)-(\d+).*")
legible_date_regex = re.compile("^.*([A-Z0][a-z]+)\s+(\d+)[,\.]\s*(\d+).*$") #the [,\.] is accounting for load.py's price_regex doing a match on the date too.
proposed_date_regex = re.compile("^.*\D(\d+)-(\d+)-(\d+).*$")
number_missing_dot_regex = re.compile("^.*(\d{2})(\d{5}).*$")
