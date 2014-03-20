import re

date_regex  = re.compile("^(\d{1,2})/(\d{1,2})/(\d{4})$")
dose_regex = re.compile("^(.*)\s(\d*\.*\d+)\s{0,1}([a-z\%]+)|(.*)\s(\d*\.*\d+[a-z\%]*\-\d*\.*\d+\s{0,1}[a-z\%]*)$")
