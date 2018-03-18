import datetime

DATE_STYLE_GUESS = 0  # use heuristics to determine component order
DATE_STYLE_DMY = 1
DATE_STYLE_MDY = 2
DATE_STYLE_YMD = 3

def to_standard_date(s, delimiter='-', style=DATE_STYLE_DMY):
    """
    Convert a string representing a date to the ISO 8601 format.
    See http://www.cl.cam.ac.uk/~mgk25/iso-time.html for details.
    """
    if delimiter == '':
        raise ValueError('Empty delimiter')
        
    year = None
    month = None
    day = None
    
    parts = s.split(delimiter)
    if len(parts) != 3:
        raise ValueError('Date must have 3 parts, not %d' % len(parts))
        
    components = map(int, parts)

    if style == DATE_STYLE_DMY:
        year = components[2]
        month = components[1]
        day = components[0]
    elif style == DATE_STYLE_MDY:
        year = components[2]
        month = components[0]
        day = components[1]
    elif style == DATE_STYLE_YMD:
        year = components[0]
        month = components[1]
        day = components[2]
        
    elif style == DATE_STYLE_GUESS:
        ambiguous = False  # raise a flag if unable to decide between day and month
        
        if components[0] > 12 and components[1] <= 12 and components[2] > 31:  # maybe DMY
            year = components[2]
            month = components[1]
            day = components[0]
            
            if month <= 12 and day <= 12:
                ambiguous = True
            
        elif components[0] <= 12 and components[1] <= 31 and components[2] > 31:  # maybe MDY
            year = components[2]
            month = components[0]
            day = components[1]

            if month <= 12 and day <= 12:
                ambiguous = True
                
        elif components[0] > 31 and components[1] <= 12 and components[2] <= 31:  # maybe YMD
            year = components[0]
            month = components[1]
            day = components[2]
        else:
            year = components[0]
            month = components[1]
            day = components[2]
            
        if ambiguous:
            raise ValueError('Date values too ambiguous to guess: %d, %d, %d' % (year, month, day))
        
    else:
        raise ValueError('Date style too weird to process')

    # For two-digit years, fix the century by looking at the years.
    # If it falls between zero and the system's current year, assume 2000's.
    # Otherwise, it is probably in the 1900's.
    if year < 100:  # we have a 2-digit year, so fix the century
        today = datetime.datetime.now()
        if year >= 0 and year <= today.year - 2000:
            year += 2000
        else:
            year += 1900

    result = '%04d-%02d-%02d' % (year, month, day)
    return result

# Test tuples: input, delimiter, date style, expected output
stddate_tests = [ ('2/4/1995', '/', DATE_STYLE_MDY, '1995-02-04'),
                  ('4/2/1995', '/', DATE_STYLE_DMY, '1995-02-04'),
                  ('1995/2/4', '/', DATE_STYLE_YMD, '1995-02-04'),
                  ('4.2.1995', '.', DATE_STYLE_DMY, '1995-02-04'),
                  ('1995-04-02', '-', DATE_STYLE_GUESS, '1995-04-02'),
                  ('2/4/95', '/', DATE_STYLE_MDY, '1995-02-04'),
                  ('4/2/95', '/', DATE_STYLE_DMY, '1995-02-04') ]

def test(tests, name=''):
    "For each test case, see if we get the expected output."
    fails = 0
    for (input, delimiter, style, expected) in tests:
        result = None
        try:
            result = to_standard_date(input, delimiter=delimiter, style=style)
            ok = (result == expected)
        except Exception as e:
            print('"%s =raises=> %s, %s' % (input, type(e).__name__, e))
            #ok = issubclass(expected, Exception) and isinstance(e, expected)
            ok = False
        if not ok:
            fails += 1
            print('FAIL! For "%s" expected "%s", got "%s"' % (input, expected, result))
            
    # Test a few special cases. These should raise a ValueError.
    try:
        print(to_standard_date('3/4/95', delimiter='/', style=DATE_STYLE_GUESS))
    except Exception as e:
        print('%s: %s' % (type(e).__name__, e))

    try:
        print(to_standard_date('4/3/95', delimiter='/', style=DATE_STYLE_GUESS))
    except Exception as e:
        print('%s: %s' % (type(e).__name__, e))
            
    if fails != 0:
        print('%s %s: %d out of %d tests fail.' % ('*'*45, name, fails, len(tests)))
    else:
        print('%s %s: All tests pass.' % ('*'*45, name))
                  
test(stddate_tests, 'stddate')
