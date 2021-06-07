import os
import json
from bentoml.utils import cloudpickle
from bentoml.exceptions import InvalidArgument
from bentoml.service.artifacts import BentoServiceArtifact
from bentoml import BentoService, env, api, artifacts
from bentoml.adapters import JsonInput
import bentoml

class MyModelArtifact(BentoServiceArtifact):
    def __init__(self, name):
        super(MyModelArtifact, self).__init__(name)
        self._model = None

    def pack(self, model, metadata=None):
        if isinstance(model, dict) is not True:
            raise InvalidArgument('MyModelArtifact only support dict')
        if model.get('foo', None) is None:
            raise KeyError('"foo" is not available in the model')
        self._model = model
        return self

    def get(self):
        return self._model

    def save(self,dst):
        with open(self._file_path(dst), 'wb') as file:
            cloudpickle.dump(self._model, file)

    def load(self, path):
        with open(self._file_path(path), 'rb') as file:
            model = cloudpickle.load(file)
        return self.pack(model)

    def _file_path(self, base_path):
        return os.path.join(base_path, self.name + '.json')

#from my_model_artifact import MyModelArtifact


@env(infer_pip_packages=True)
@artifacts([MyModelArtifact('test_model')])
class MyService(bentoml.BentoService):

    @api(input=JsonInput(), batch=False)
    def predict(input_data):

        result =  self.artifacts.test_model['bar']
        #return input_data['foo'],self.artifacts.test_model['bar']
        return {'result': result}

#from my_bento_service import MyService

svc = MyService()
model = {'foo': 2}
svc.pack('test_model', model)
svc.save()