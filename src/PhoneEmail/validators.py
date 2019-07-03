import re
	
non_phone_number_element_regex_finder = re.compile(
    r'[a-zA-z!@#$%^&*()+=|~`{}-]')