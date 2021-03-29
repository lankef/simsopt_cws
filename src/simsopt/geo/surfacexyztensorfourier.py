import numpy as np
import simsgeopp as sgpp
from .surface import Surface
from .surfacerzfourier import SurfaceRZFourier


class SurfaceXYZTensorFourier(sgpp.SurfaceXYZTensorFourier, Surface):
    def __init__(self, nfp=1, stellsym=True, mpol=1, ntor=1, quadpoints_phi=32, quadpoints_theta=32):
        if isinstance(quadpoints_phi, np.ndarray):
            quadpoints_phi = list(quadpoints_phi)
            quadpoints_theta = list(quadpoints_theta)
        sgpp.SurfaceXYZTensorFourier.__init__(self, mpol, ntor, nfp, stellsym, quadpoints_phi, quadpoints_theta)
        self.x[0, 0] = 1.0
        self.x[1, 0] = 0.1
        self.z[mpol+1, 0] = 0.1
        Surface.__init__(self)

    def get_dofs(self):
        return np.asarray(sgpp.SurfaceXYZTensorFourier.get_dofs(self))

    def to_RZFourier(self):
        surf = SurfaceRZFourier(self.mpol, self.ntor, self.nfp, self.stellsym, self.quadpoints_phi, self.quadpoints_theta)
        surf.least_squares_fit(self.gamma())
        return surf

    def set_dofs(self, dofs):
        sgpp.SurfaceXYZTensorFourier.set_dofs(self, dofs)
        for d in self.dependencies:
            d.invalidate_cache()
