import json

from docker import AutoVersionClient
from loguru import logger
from yoyo.targets.base.cmds import TargetCmds
from yoyo.utils import cd_python


class CloudRunCmds(TargetCmds):
    def up(self):
        """Run service locally"""
        for service in self.services:
            # docker build -t gcr.io/query-router/client-config-store .
            # docker push gcr.io/query-router/client-config-store
            # gcloud run deploy client-config-store \
            # 		--image gcr.io/query-router/client-config-store \
            # 		--platform managed \
            # 		--region europe-west1
            logger.info(f"Building '{service}'...")
            client = AutoVersionClient()
            output = client.build(
                path=str(self._absolute_paths.service_dir(service)),
                tag=f'gcr.io/query-router/{service}',
                dockerfile=str(self._absolute_paths.root / 'services/Dockerfile')
            )
            for lines in output:
                for line in str(lines, 'utf-8').split('\n'):
                    line = line.strip(" \r")
                    if not line:
                        continue
                    log = json.loads(line)
                    if stream := log.get('stream', None):
                        logger.debug(stream.strip('\n '))
                    if error := log.get('errorDetail', None):
                        logger.error(error['message'].strip('\n '))
