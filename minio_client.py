import os
from minio import Minio
from core.config import main_logger

""" UMS Minio client module

Example:
mc = UMS_Minio(product_id='1793')
mc.upload_file('render_log.txt', '8253', '9152', '3071')
mc.upload_file('overall_log_suite.txt', '8253', '9152')
mc.upload_file('build.dmg', '8253')

"""

class UMS_Minio:
    # TODO: access + secret + url to env
    def __init__(self,
            product_id,
            enpoint='172.31.27.8:9000',
            access_key='123456789',
            secret_key='123456789'
        ):
        self.mc = Minio(enpoint, access_key, secret_key, secure=False)
        self.bucket_name = str(product_id).lower()
        self.__save_bucket_if_not_exits()

    def __save_bucket_if_not_exits(self):
        """ Provat method for check bucket existance by name
        """
        if not self.mc.bucket_exists(self.bucket_name):
            self.mc.make_bucket(self.bucket_name)

    def upload_file(self, fname, *args):
        """ Method for upload file to storage
        
        @Arguments:
        fname - file name (log.txt)
        args - (build_id, tsr_id, tcr_id)
        """
        
        # generate artefact name PATH/TO/FILE.EXT
        artefac_name = "/".join(args) + "/" + fname
        try:
            file_size = os.stat(fname).st_size
            with open(fname, 'rb') as data:
                self.mc.put_object(
                    bucket_name=self.bucket_name,
                    object_name=artefac_name,
                    data=data,
                    length=file_size
                )
        except FileNotFoundError as e:
            print(e)
            main_logger.error(str(e))

mc = UMS_Minio(product_id='1793')
mc.upload_file('render_log.txt', '8253', '9152', '3071')
mc.upload_file('overall_log_suite.txt', '8253', '9152')
mc.upload_file('build.dmg', '8253')