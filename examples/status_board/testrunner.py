from django.test.simple import DjangoTestSuiteRunner
from mongoengine.connection import connect, disconnect, get_connection

class WhiskerboardTestRunner(DjangoTestSuiteRunner):
    def setup_databases(self, **kwargs):
        disconnect()
        connect('test_whiskerboard')
        return super(WhiskerboardTestRunner, self).setup_databases(**kwargs)
        
    def teardown_databases(self, old_config, **kwargs):
        connection = get_connection()
        connection.drop_database('test_whiskerboard')
        disconnect()
        super(WhiskerboardTestRunner, self).teardown_databases(old_config, **kwargs)
    

    def build_suite(self, test_labels, *args, **kwargs):
        return super(WhiskerboardTestRunner, self).build_suite(['whiskerboard'], *args, **kwargs)
