import os
import sys

def bootstrap(path):
    """
    Call this function as the first thing in your cron, or console script; it will bootstrap Django, and allow you to access all of the Django modules from the console, without using 'python manage.py shell'

    Examples:
 
        # A script within your django project.
        from django_bootstrap import bootstrap
        bootstrap(__file__) 
    
    --- or ---
    
        # A cron script located outside of your django project
        from django_bootstrap import bootstrap
        bootstrap("/path/to/your/project/root/")
    """
    path = find_settings_path(path)
    parent_path = os.path.abspath(os.path.join(path, '..'))
    
    # Include path to settings.py directory
    os.sys.path.append(path)
    # Include path to django project directory
    os.sys.path.append(parent_path)
    
    from django.core import management
    try:
        import settings # Assumed to be in the os path
    except ImportError:
        sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
        sys.exit(1)
        
    management.setup_environ(settings)

def find_settings_path(path):
    """
    Retrieve the path of the settings.py module for a django project. This can be passed into django_utils.bootstrap). You can pass in the  __file__ variable, or an absolute path, and it will find the closest settings.py module.
    """
    if os.path.isfile(path):
        path = os.path.dirname(path)
    
    path = os.path.abspath(path)
    parent_path = os.path.abspath(os.path.join(path, '..'))
    settings_path = os.path.join(path, 'settings.py')

    if os.path.exists(settings_path):
        return path
    elif path != parent_path:
        return find_settings_path(parent_path)
    else:
        raise Exception('Could not find settings path.')

