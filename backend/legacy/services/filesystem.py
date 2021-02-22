from . import BaseService
try:
    from ..db import Filesystem
except:
    from db import Filesystem


class FilesystemService(BaseService):
    model = Filesystem

    def get_all_filesystem_name(self):
        return [data[0] for data in self.session.query(self.model.name).all()]

    def get_or_create_filesystem(self, name):
        session = self.session
        model = session.query(Filesystem).filter(Filesystem.name == name).first()
        if not model:
            model = Filesystem(name=name)
            from .package import PackageService
            model.package_id = PackageService().create_package('root').id
            session.add(model)
            session.commit()
        return model

    def get_filesystem_by_name(self, name):
        session = self.session
        model = session.query(Filesystem).filter(Filesystem.name == name).first()
        return model
