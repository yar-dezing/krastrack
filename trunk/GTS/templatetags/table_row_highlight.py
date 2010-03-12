"Tag which highlights even/odd table rows with specified color"

from django import template

register = template.Library()

#------------------------------------------------------------------------------ 
@register.simple_tag
def odd_even_row(counter, odd_row, even_row):
    '''
    PARAMETERS:
    counter           - for loop counter
    odd_row, even_row - CSS classes names
    
    Gets two CSS classes - for even and odd rows. 
    Returns CSS class name (string).
    '''
    
    if counter % 2 == 0:
        return even_row
    else:
        return odd_row

#------------------------------------------------------------------------------ 

