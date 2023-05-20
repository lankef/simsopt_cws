from pathlib import Path
import unittest

import numpy as np
import simsoptpp as sopp

from simsopt.field import (BiotSavart, Current, DipoleField, InterpolatedField,
                           coils_via_symmetries, Coil)
from simsopt.geo import (PermanentMagnetGrid, SurfaceRZFourier, SurfaceXYZFourier,
                         create_equally_spaced_curves)
from simsopt.objectives import SquaredFlux
from simsopt.solve import GPMO, relax_and_split
from simsopt.util import *
from simsopt.util.polarization_project import *

#from . import TEST_DIR
TEST_DIR = (Path(__file__).parent / ".." / "test_files").resolve()

# File for the desired boundary magnetic surface:
filename = TEST_DIR / 'input.LandremanPaul2021_QA'


class Testing(unittest.TestCase):

    def test_bad_params(self):
        """
            Test that the permanent magnet optimizer initialization
            correctly catches bad instances of the function arguments.
        """
        nphi = 32
        ntheta = 32
        Bn = np.zeros((nphi, ntheta))
        s = SurfaceRZFourier.from_vmec_input(filename, range="half period", nphi=nphi, ntheta=ntheta)
        s1 = SurfaceRZFourier.from_vmec_input(filename, range="half period", nphi=nphi, ntheta=ntheta)
        s2 = SurfaceRZFourier.from_vmec_input(filename, range="half period", nphi=nphi, ntheta=ntheta)
        s3 = SurfaceXYZFourier(nfp=2, stellsym=True)
        s1.extend_via_projected_normal(0.1)
        s2.extend_via_projected_normal(0.2)
        PermanentMagnetGrid(
            s3, Bn, 
        )

        with self.assertRaises(ValueError):
            PermanentMagnetGrid(
                s, Bn, dr=-0.05 
            )
        with self.assertRaises(TypeError):
            PermanentMagnetGrid(
                s,
            )
        with self.assertRaises(ValueError):
            PermanentMagnetGrid(
                s, Bn, Nx=-2 
            )
        with self.assertRaises(TypeError):
            pm_opt = PermanentMagnetGrid(
                s, Bn,
            )
            pm_opt.geo_setup_between_toroidal_surfaces() 
        with self.assertRaises(ValueError):
            PermanentMagnetGrid(
                s, Bn, dz=-0.05
            )
        with self.assertRaises(TypeError):
            PermanentMagnetGrid(
                10,
            )
        with self.assertRaises(ValueError):
            PermanentMagnetGrid(
                s, Bn, coordinate_flag='cylindrical',
            )
            pm_opt.geo_setup_between_toroidal_surfaces(s1, s2, pol_vectors=[10])
        with self.assertRaises(ValueError):
            PermanentMagnetGrid(
                s, Bn=0.0 
            )
        with self.assertRaises(ValueError):
            pm = PermanentMagnetGrid(
                s, Bn=np.zeros((nphi, ntheta // 2))
            )
            pm.geo_setup_between_toroidal_surfaces(s1, s2)
        with self.assertRaises(ValueError):
            pm = PermanentMagnetGrid(
                s, Bn=Bn
            )
            pm.geo_setup_between_toroidal_surfaces(s1, s2, m_maxima=np.ones(4))
        with self.assertRaises(ValueError):
            pm = PermanentMagnetGrid(
                s, Bn=np.zeros((nphi, ntheta))
            )
            pm.geo_setup_from_famus(TEST_DIR / 'zot80.log')
        with self.assertRaises(ValueError):
            pm = PermanentMagnetGrid(
                s, Bn=np.zeros((nphi, ntheta))
            )
            pm.geo_setup_from_famus(TEST_DIR / 'zot80.focus', m_maxima=np.ones(4))
        with self.assertRaises(ValueError):
            pm = PermanentMagnetGrid(
                s, Bn=np.zeros((nphi, ntheta))
            )
            pm.geo_setup_between_toroidal_surfaces(s1, s2, pol_vectors=np.ones((5, 3, 2)))
        with self.assertRaises(ValueError):
            pm = PermanentMagnetGrid(
                s, Bn=np.zeros((nphi, ntheta)),
            )
            pm.geo_setup_between_toroidal_surfaces(s1, s2, pol_vectors=np.ones((5, 3)))
        with self.assertRaises(ValueError):
            pm = PermanentMagnetGrid(
                s, Bn=np.zeros((nphi, ntheta)), coordinate_flag='cylindrical'
            )
            pm.geo_setup_between_toroidal_surfaces(s1, s2, pol_vectors=np.ones((5, 3, 3)))
        with self.assertRaises(NotImplementedError):
            pm = PermanentMagnetGrid(
                s, Bn=np.zeros((nphi, ntheta)), coordinate_flag='random_name'
            )

    def test_optimize_bad_parameters(self):
        """
            Test that the permanent magnet optimize
            correctly catches bad instances of the function arguments.
        """
        nphi = 32
        ntheta = 32
        s = SurfaceRZFourier.from_vmec_input(filename, range="half period", nphi=nphi, ntheta=ntheta)
        s1 = SurfaceRZFourier.from_vmec_input(filename, range="half period", nphi=nphi, ntheta=ntheta)
        s2 = SurfaceRZFourier.from_vmec_input(filename, range="half period", nphi=nphi, ntheta=ntheta)
        s1.extend_via_projected_normal(0.1)
        s2.extend_via_projected_normal(0.2)

        # Create some initial coils:
        base_curves = create_equally_spaced_curves(2, s.nfp, stellsym=False, R0=1.0, R1=0.5, order=5)
        base_currents = [Current(1e5) for i in range(2)]
        coils = coils_via_symmetries(base_curves, base_currents, s.nfp, True)
        bs = BiotSavart(coils)
        bs.set_points(s.gamma().reshape((-1, 3)))

        # Create PM class
        Bn = np.sum(bs.B().reshape(nphi, ntheta, 3) * s.unitnormal(), axis=-1)
        pm_opt = PermanentMagnetGrid(s, dr=0.15, Bn=Bn)
        pm_opt.geo_setup_between_toroidal_surfaces(s1, s2)

        # Note that the rest of the optimization parameters are checked
        # interactively when python permanent_magnet_optimization.py True 
        # is used on the command line. 
        with self.assertRaises(ValueError):
            _, _, _, _, = relax_and_split(pm_opt)

        with self.assertRaises(ValueError):
            _, _, _, = relax_and_split(pm_opt, m0=np.zeros(pm_opt.ndipoles * 3 // 2))

        with self.assertRaises(ValueError):
            _, _, _, = relax_and_split(pm_opt, m0=np.zeros((pm_opt.ndipoles, 3)))

        with self.assertRaises(ValueError):
            mmax = np.ravel(np.array([pm_opt.m_maxima, pm_opt.m_maxima, pm_opt.m_maxima]).T)
            _, _, _, = relax_and_split(pm_opt, m0=np.ones((pm_opt.ndipoles * 3)) * mmax)

        kwargs = {}
        kwargs['verbose'] = False
        GPMO(pm_opt, algorithm='baseline', **kwargs)

        kwargs = initialize_default_kwargs('GPMO')
        kwargs['verbose'] = False
        with self.assertRaises(ValueError):
            GPMO(pm_opt, algorithm='backtracking', **kwargs)

        with self.assertRaises(ValueError):
            GPMO(pm_opt, algorithm='multi', **kwargs)

    def test_projected_normal(self):
        """
            Make two RZFourier surfaces, extend one of them with
            the projected normal vector in the RZ plane, and check
            that both surfaces still have the same values of the
            toroidal angle. 
        """
        nphi = 32
        ntheta = 32
        s = SurfaceRZFourier.from_vmec_input(filename, range="half period", nphi=nphi, ntheta=ntheta)
        p = SurfaceRZFourier.from_vmec_input(filename, range="half period", nphi=nphi, ntheta=ntheta)
        s.extend_via_projected_normal(0.1)
        pgamma = p.gamma().reshape(-1, 3)
        pphi = np.arctan2(pgamma[:, 1], pgamma[:, 0])
        sgamma = s.gamma().reshape(-1, 3)
        sphi = np.arctan2(sgamma[:, 1], sgamma[:, 0])
        assert np.allclose(pphi, sphi)
        assert not np.allclose(pgamma[:, 0], sgamma[:, 0])
        assert not np.allclose(pgamma[:, 1], sgamma[:, 1])
        assert not np.allclose(pgamma[:, 2], sgamma[:, 2])

    def test_Bn(self):
        """
            Creates a realistic QA configuration, some permanent magnets, and optimizes it
            with the default parameters. Checks the the pm_opt object agrees with Bn and
            f_B with the DipoleField + SquaredFlux way of calculating Bn and f_B.
        """
        nphi = 32
        ntheta = 32
        s = SurfaceRZFourier.from_vmec_input(filename, range="half period", nphi=nphi, ntheta=ntheta)
        s1 = SurfaceRZFourier.from_vmec_input(filename, range="half period", nphi=nphi, ntheta=ntheta)
        s2 = SurfaceRZFourier.from_vmec_input(filename, range="half period", nphi=nphi, ntheta=ntheta)
        s1.extend_via_projected_normal(0.1)
        s2.extend_via_projected_normal(0.2)

        # Create some initial coils:
        base_curves = create_equally_spaced_curves(2, s.nfp, stellsym=False, R0=1.0, R1=0.5, order=5)
        base_currents = [Current(1e5) for i in range(2)]
        coils = coils_via_symmetries(base_curves, base_currents, s.nfp, True)
        bs = BiotSavart(coils)
        bs.set_points(s.gamma().reshape((-1, 3)))

        # Create PM class
        Bn = np.sum(bs.B().reshape(nphi, ntheta, 3) * s.unitnormal(), axis=-1)
        pm_opt = PermanentMagnetGrid(s, dr=0.15, Bn=Bn)
        pm_opt.geo_setup_between_toroidal_surfaces(s1, s2)
        _, _, _, = relax_and_split(pm_opt)
        b_dipole = DipoleField(
            pm_opt.dipole_grid_xyz,
            pm_opt.m_proxy,
            nfp=s.nfp,
            coordinate_flag=pm_opt.coordinate_flag,
            m_maxima=pm_opt.m_maxima,
        )
        b_dipole.set_points(s.gamma().reshape(-1, 3))

        # check Bn
        Nnorms = np.ravel(np.sqrt(np.sum(s.normal() ** 2, axis=-1)))
        Ngrid = nphi * ntheta
        Bn_Am = (pm_opt.A_obj.dot(pm_opt.m) - pm_opt.b_obj) * np.sqrt(Ngrid / Nnorms) 
        assert np.allclose(Bn_Am.reshape(nphi, ntheta), np.sum((bs.B() + b_dipole.B()).reshape((nphi, ntheta, 3)) * s.unitnormal(), axis=2))

        # check <Bn>
        B_opt = np.mean(np.abs(pm_opt.A_obj.dot(pm_opt.m) - pm_opt.b_obj) * np.sqrt(Ngrid / Nnorms))
        B_dipole_field = np.mean(np.abs(np.sum((bs.B() + b_dipole.B()).reshape((nphi, ntheta, 3)) * s.unitnormal(), axis=2)))
        assert np.isclose(B_opt, B_dipole_field)

        # check integral Bn^2
        f_B_Am = 0.5 * np.linalg.norm(pm_opt.A_obj.dot(pm_opt.m) - pm_opt.b_obj, ord=2) ** 2
        f_B = SquaredFlux(s, b_dipole, -Bn).J()
        assert np.isclose(f_B, f_B_Am)

        # Create PM class with cylindrical bricks
        Bn = np.sum(bs.B().reshape(nphi, ntheta, 3) * s.unitnormal(), axis=-1)
        pm_opt = PermanentMagnetGrid(s, dr=0.15, Bn=Bn, coordinate_flag='cylindrical')
        pm_opt.geo_setup_between_toroidal_surfaces(s1, s2)
        mmax_new = pm_opt.m_maxima / 2.0
        pm_opt.geo_setup_between_toroidal_surfaces(s1, s2, m_maxima=mmax_new)
        assert np.allclose(pm_opt.m_maxima, mmax_new)
        mmax_new = pm_opt.m_maxima[-1] / 2.0
        pm_opt.geo_setup_between_toroidal_surfaces(s1, s2, m_maxima=mmax_new)
        assert np.allclose(pm_opt.m_maxima, mmax_new)
        pm_opt.geo_setup_between_toroidal_surfaces(s1, s2)
        _, _, _, = relax_and_split(pm_opt)
        b_dipole = DipoleField(
            pm_opt.dipole_grid_xyz,
            pm_opt.m_proxy,
            nfp=s.nfp,
            coordinate_flag=pm_opt.coordinate_flag,
            m_maxima=pm_opt.m_maxima,
        )
        b_dipole.set_points(s.gamma().reshape(-1, 3))

        # check Bn
        Nnorms = np.ravel(np.sqrt(np.sum(s.normal() ** 2, axis=-1)))
        Ngrid = nphi * ntheta
        Bn_Am = (pm_opt.A_obj.dot(pm_opt.m) - pm_opt.b_obj) * np.sqrt(Ngrid / Nnorms) 
        assert np.allclose(Bn_Am.reshape(nphi, ntheta), np.sum((bs.B() + b_dipole.B()).reshape((nphi, ntheta, 3)) * s.unitnormal(), axis=2))

        # check <Bn>
        B_opt = np.mean(np.abs(pm_opt.A_obj.dot(pm_opt.m) - pm_opt.b_obj) * np.sqrt(Ngrid / Nnorms))
        B_dipole_field = np.mean(np.abs(np.sum((bs.B() + b_dipole.B()).reshape((nphi, ntheta, 3)) * s.unitnormal(), axis=2)))
        assert np.isclose(B_opt, B_dipole_field)

        # check integral Bn^2
        f_B_Am = 0.5 * np.linalg.norm(pm_opt.A_obj.dot(pm_opt.m) - pm_opt.b_obj, ord=2) ** 2
        f_B = SquaredFlux(s, b_dipole, -Bn).J()
        assert np.isclose(f_B, f_B_Am)

    def test_grid_chopping(self):
        """
            Makes a tokamak, extends two toroidal surfaces from this surface, and checks
            that the grid chopping function correctly removes magnets that are not between
            the inner and outer surfaces.
        """
        filename = TEST_DIR / 'input.circular_tokamak'
        nphi = 32
        ntheta = 32
        contig = np.ascontiguousarray
        s = SurfaceRZFourier.from_vmec_input(filename, range="full torus", nphi=nphi, ntheta=ntheta)
        s1 = SurfaceRZFourier.from_vmec_input(filename, range="full torus", nphi=nphi, ntheta=ntheta)
        s2 = SurfaceRZFourier.from_vmec_input(filename, range="full torus", nphi=nphi, ntheta=ntheta)
        s1.extend_via_projected_normal(1)
        s2.extend_via_projected_normal(2)

        # Generate uniform grid
        R0 = s.get_rc(0, 0)  # major radius
        r0 = s.get_rc(1, 0)  # minor radius
        r = np.linspace(0, 5, 10)
        theta = np.linspace(0, 2 * np.pi, 10)
        phi = np.linspace(0, 2 * np.pi, 10)
        r, phi, theta = np.meshgrid(r, phi, theta, indexing='ij')
        R = R0 + r * np.cos(theta)
        Z = r * np.sin(theta)
        X = R * np.cos(phi)
        Y = R * np.sin(phi)
        RphiZ = np.array([R, phi, Z]).T.reshape(-1, 3)
        XYZ = np.array([X, Y, Z]).T.reshape(-1, 3)
        normal_inner = s1.unitnormal().reshape(-1, 3)   
        normal_outer = s2.unitnormal().reshape(-1, 3)
        xyz_inner = s1.gamma().reshape(-1, 3)
        xyz_outer = s2.gamma().reshape(-1, 3)
        r_inner = np.sqrt(xyz_inner[:, 0] ** 2 + xyz_inner[:, 1] ** 2)
        z_inner = xyz_inner[:, 2]
        r_outer = np.sqrt(xyz_outer[:, 0] ** 2 + xyz_outer[:, 1] ** 2)
        z_outer = xyz_outer[:, 2]

        # Try with cylindrical functionality 
        grid, inds = sopp.define_a_uniform_cylindrical_grid_between_two_toroidal_surfaces(
            contig(phi), 
            contig(normal_inner), 
            contig(normal_outer),
            contig(RphiZ), 
            contig(r_inner), 
            contig(r_outer), 
            contig(z_inner), 
            contig(z_outer)
        )
        inds = np.array(inds, dtype=int)
        for i in reversed(range(1, len(inds))):
            for j in range(0, i):
                inds[i] += inds[j]
        final_grid = []
        for i in range(grid.shape[0]):
            if not np.allclose(grid[i, :], 0.0):
                final_grid.append(grid[i, :])
        final_grid = np.array(final_grid)
        r_fit = np.sqrt((final_grid[:, 0] - R0) ** 2 + final_grid[:, 2] ** 2)
        # print('r_fit = ', r_fit)
        assert (np.min(r_fit) > (r0 + 1.0))
        assert (np.max(r_fit) < (r0 + 2.0))

        # Repeat with cartesian functionality
        XYZ = np.array([X, Y, Z]).T.reshape(-1, 3)
        normal_inner = s1.unitnormal().reshape(-1, 3)   
        normal_outer = s2.unitnormal().reshape(-1, 3)
        xyz_inner = s1.gamma().reshape(-1, 3)
        xyz_outer = s2.gamma().reshape(-1, 3)
        final_grid = sopp.define_a_uniform_cartesian_grid_between_two_toroidal_surfaces(
            contig(normal_inner), 
            contig(normal_outer), 
            contig(XYZ), 
            contig(xyz_inner), 
            contig(xyz_outer)
        )
        inds = np.ravel(np.logical_not(np.all(final_grid == 0.0, axis=-1)))
        final_grid = final_grid[inds, :]
        final_rz_grid = np.zeros(final_grid.shape)
        final_rz_grid[:, 0] = np.sqrt(final_grid[:, 0] ** 2 + final_grid[:, 1] ** 2)
        final_rz_grid[:, 1] = np.arctan2(final_grid[:, 1], final_grid[:, 0])
        final_rz_grid[:, 2] = final_grid[:, 2] 
        r_fit = np.sqrt((final_rz_grid[:, 0] - R0) ** 2 + final_rz_grid[:, 2] ** 2)
        assert (np.min(r_fit) > (r0 + 1.0))
        assert (np.max(r_fit) < (r0 + 2.0))

    def test_famus_functionality(self):
        """
            Tests the FocusData and FocusPlasmaBnormal classes 
            and class functions. 
        """
        fname_plasma = TEST_DIR / 'c09r00_B_axis_half_tesla_PM4Stell.plasma'
        bnormal_obj_ncsx = FocusPlasmaBnormal(fname_plasma)
        bn_plasma = bnormal_obj_ncsx.bnormal_grid(8, 8, 'half period')
        assert bn_plasma.shape == (8, 8)
        assert np.allclose(bnormal_obj_ncsx.bnc, 0.0)
        bnormal_obj_ncsx.stellsym = False
        bnormal_obj_ncsx.bnc = bnormal_obj_ncsx.bns
        bn_plasma = bnormal_obj_ncsx.bnormal_grid(8, 8, 'field period')
        assert bn_plasma.shape == (8, 8)

        mag_data = FocusData(TEST_DIR / 'zot80.focus')
        for i in range(mag_data.nMagnets):
            assert np.isclose(np.dot(np.array(mag_data.perp_vector([i])).T, np.array(mag_data.unit_vector([i]))), 0.0)

        with self.assertRaises(Exception):
            mag_data.perp_vector([mag_data.nMagnets])
        with self.assertRaises(Exception):
            mag_data.unit_vector([mag_data.nMagnets])

        assert (np.sum(mag_data.pho < 0) > 0)
        with self.assertRaises(RuntimeError):
            mag_data.adjust_rho(4.0)
        mag_data.flip_negative_magnets()
        mag_data.flip_negative_magnets()
        assert (np.sum(mag_data.pho < 0) == 0)
        mag_data.adjust_rho(4.0)
        assert mag_data.momentq == 4.0
        mag_data.has_momentq = False
        mag_data.adjust_rho(3.0)
        assert mag_data.momentq == 3.0
        mag_data.print_to_file('test')
        mag_data.has_momentq = False
        mag_data.has_op = True
        mag_data.op = mag_data.oz
        mag_data.print_to_file('test')
        nMag = mag_data.nMagnets
        mag_data.nMagnets = 0
        with self.assertRaises(RuntimeError):
            mag_data.print_to_file('test')
        mag_data.nMagnets = nMag
        mag_data.init_pol_vecs(3)
        assert mag_data.pol_x.shape == (mag_data.nMagnets, 3)
        assert mag_data.pol_y.shape == (mag_data.nMagnets, 3)
        assert mag_data.pol_z.shape == (mag_data.nMagnets, 3)
        nMagnets = mag_data.nMagnets
        mag_data.repeat_hp_to_fp(nfp=2, magnet_sector=1)
        assert mag_data.nMagnets == nMagnets * 2
        assert np.allclose(mag_data.oz[:mag_data.nMagnets // 2], -mag_data.oz[mag_data.nMagnets // 2:])
        with self.assertRaises(ValueError):
            mag_data.repeat_hp_to_fp(nfp=2, magnet_sector=10)
        mag_data.symm = 1 * np.ones(len(mag_data.symm))
        with self.assertRaises(ValueError):
            mag_data.repeat_hp_to_fp(nfp=2, magnet_sector=1)
        mag_data.symm = 2 * np.ones(len(mag_data.symm))
        phi0 = np.pi / 2
        ox2, oy2, oz2 = stell_point_transform('reflect', phi0, mag_data.ox, mag_data.oy, mag_data.oz)
        assert np.allclose(mag_data.oz, -oz2)
        ox2, oy2, oz2 = stell_point_transform('translate', phi0, mag_data.ox, mag_data.oy, mag_data.oz)
        assert np.allclose(mag_data.oz, oz2)
        symm_inds = np.where(mag_data.symm == 2)[0]
        nx, ny, nz = mag_data.unit_vector(symm_inds)
        nx2, ny2, nz2 = stell_vector_transform('reflect', phi0, nx, ny, nz)
        assert np.allclose(nz, nz2)
        assert np.allclose(nx ** 2 + ny ** 2 + nz ** 2, nx2 ** 2 + ny2 ** 2 + nz2 ** 2)
        nx2, ny2, nz2 = stell_vector_transform('translate', phi0, nx, ny, nz)
        assert np.allclose(nz, nz2)
        assert np.allclose(nx ** 2 + ny ** 2 + nz ** 2, nx2 ** 2 + ny2 ** 2 + nz2 ** 2)
        with self.assertRaises(ValueError):
            nx2, ny2, nz2 = stell_vector_transform('random', phi0, nx, ny, nz)
        with self.assertRaises(ValueError):
            nx2, ny2, nz2 = stell_point_transform('random', phi0, mag_data.ox, mag_data.oy, mag_data.oz)

    def test_polarizations(self):
        """
            Tests the polarizations and related functions from the
            polarization_project file. 
        """
        theta = 0.0 
        vecs = faceedge_vectors(theta)
        assert np.allclose(np.linalg.norm(vecs, axis=-1), 1.0)
        vecs = facecorner_vectors(theta)
        assert np.allclose(np.linalg.norm(vecs, axis=-1), 1.0)
        theta = np.pi / 6.0
        assert np.allclose(pol_fe30, faceedge_vectors(theta))
        theta = np.pi / 8.0
        assert np.allclose(pol_fe23, faceedge_vectors(theta))
        theta = 17.0 * np.pi / 180.0
        assert np.allclose(pol_fe17, faceedge_vectors(theta))
        theta = 27.0 * np.pi / 180.0
        assert np.allclose(pol_fc27, facecorner_vectors(theta))
        theta = 39.0 * np.pi / 180.0
        assert np.allclose(pol_fc39, facecorner_vectors(theta))
        assert np.allclose(np.concatenate((pol_f, faceedge_vectors(theta),
                           facecorner_vectors(theta)), axis=0
                                          ), face_triplet(theta, theta))
        assert np.allclose(np.concatenate((pol_e, faceedge_vectors(theta),
                           facecorner_vectors(theta)), axis=0
                                          ), edge_triplet(theta, theta))
        pol_axes, _ = polarization_axes('face')
        assert np.allclose(pol_f, pol_axes)
        pol_axes, _ = polarization_axes('edge')
        assert np.allclose(pol_e, pol_axes)
        pol_axes, _ = polarization_axes('corner')
        assert np.allclose(pol_c, pol_axes)
        pol_axes, _ = polarization_axes('faceedge')
        assert np.allclose(pol_fe, pol_axes)
        pol_axes, _ = polarization_axes('facecorner')
        assert np.allclose(pol_fc, pol_axes)
        pol_axes, _ = polarization_axes('edgecorner')
        assert np.allclose(pol_ec, pol_axes)
        pol_axes, _ = polarization_axes('fe17')
        assert np.allclose(pol_fe17, pol_axes)
        pol_axes, _ = polarization_axes('fe23')
        assert np.allclose(pol_fe23, pol_axes)
        pol_axes, _ = polarization_axes('fe30')
        assert np.allclose(pol_fe30, pol_axes)
        pol_axes, _ = polarization_axes('fc27')
        assert np.allclose(pol_fc27, pol_axes)
        pol_axes, _ = polarization_axes('fc39')
        assert np.allclose(pol_fc39, pol_axes)
        pol_axes, _ = polarization_axes('ec23')
        assert np.allclose(pol_ec23, pol_axes)
        theta = 38.12 * np.pi / 180.0 
        vectors = facecorner_vectors(theta)
        pol_axes, _ = polarization_axes('fc_ftri')
        assert np.allclose(vectors, pol_axes)
        theta = 30.35 * np.pi / 180.0 
        vectors = faceedge_vectors(theta)
        pol_axes, _ = polarization_axes('fe_ftri')
        assert np.allclose(vectors, pol_axes)
        theta = 18.42 * np.pi / 180.0 
        vectors = faceedge_vectors(theta)
        pol_axes, _ = polarization_axes('fe_etri')
        assert np.allclose(vectors, pol_axes)
        theta = 38.56 * np.pi / 180.0 
        vectors = facecorner_vectors(theta)
        pol_axes, _ = polarization_axes('fc_etri')
        assert np.allclose(vectors, pol_axes)
        vec_shape = np.shape(vectors)[0]
        pol_axes, pol_types = polarization_axes(['fc_ftri', 'fc_etri'])
        assert np.allclose(pol_types, np.ravel(np.array([np.ones(vec_shape), 2 * np.ones(vec_shape)])))
        pol_axes, pol_types = polarization_axes(['face', 'fc_ftri', 'fe_ftri'])
        mag_data = FocusData(TEST_DIR / 'zot80.focus')
        mag_data.init_pol_vecs(len(pol_axes))
        ox = mag_data.ox
        oy = mag_data.oy
        oz = mag_data.oz
        premade_dipole_grid = np.array([ox, oy, oz]).T
        ophi = np.arctan2(premade_dipole_grid[:, 1], premade_dipole_grid[:, 0])
        cyl_r = mag_data.cyl_r
        discretize_polarizations(mag_data, ophi, pol_axes, pol_types)
        assert not np.allclose(mag_data.cyl_r, cyl_r)
        fname_corn = TEST_DIR / 'magpie_trial104b_corners_PM4Stell.csv'
        ophi = orientation_phi(fname_corn) + np.pi
        assert (np.all(ophi <= 2 * np.pi) and np.all(ophi >= 0.0))

    def test_pm_helpers(self):
        """
            Test the helper functions in utils/permanent_magnet_helpers.py.
        """

        # Test build of the MUSE coils
        input_name = 'input.muse'
        nphi = 8
        ntheta = nphi
        surface_filename = TEST_DIR / input_name
        s = SurfaceRZFourier.from_focus(surface_filename, range="half period", nphi=nphi, ntheta=ntheta)
        s_inner = SurfaceRZFourier.from_focus(surface_filename, range="half period", nphi=nphi, ntheta=ntheta)
        s_outer = SurfaceRZFourier.from_focus(surface_filename, range="half period", nphi=nphi, ntheta=ntheta)
        s_inner.extend_via_projected_normal(0.1)
        s_outer.extend_via_projected_normal(0.2)
        base_curves, base_currents, ncoils = read_focus_coils(TEST_DIR / 'muse_tf_coils.focus')
        coils = []
        for i in range(ncoils):
            coils.append(Coil(base_curves[i], base_currents[i]))
        base_currents[0].fix_all()

        # fix all the coil shapes
        for i in range(ncoils):
            base_curves[i].fix_all()
        bs = BiotSavart(coils)

        # Calculate average, approximate on-axis B field strength
        B0avg = calculate_on_axis_B(bs, s)
        assert np.allclose(B0avg, 0.15)

        # Check coil initialization for some common stellarators wout_LandremanPaul2021_QA_lowres
        s = SurfaceRZFourier.from_wout(TEST_DIR / 'wout_LandremanPaul2021_QA_lowres.nc', range="half period", nphi=nphi, ntheta=ntheta)
        base_curves, curves, coils = initialize_coils('qa', TEST_DIR, '', s)
        bs = BiotSavart(coils)
        B0avg = calculate_on_axis_B(bs, s)
        assert np.allclose(B0avg, 0.15)

        s = SurfaceRZFourier.from_wout(TEST_DIR / 'wout_LandremanPaul2021_QH_reactorScale_lowres_reference.nc', range="half period", nphi=nphi, ntheta=ntheta)
        base_curves, curves, coils = initialize_coils('qh', TEST_DIR, '', s)
        bs = BiotSavart(coils)
        B0avg = calculate_on_axis_B(bs, s)
        assert np.allclose(B0avg, 0.15)

        # Repeat with wrapper function
        s = SurfaceRZFourier.from_focus(surface_filename, range="half period", nphi=nphi, ntheta=ntheta)
        base_curves, curves, coils = initialize_coils('muse_famus', TEST_DIR, '', s)
        bs = BiotSavart(coils)
        B0avg = calculate_on_axis_B(bs, s)
        assert np.allclose(B0avg, 0.15)

        # Test rescaling
        pm_opt = PermanentMagnetGrid(
            s,
            Bn=np.zeros((nphi, ntheta)), 
        )
        pm_opt.geo_setup_between_toroidal_surfaces(s_inner, s_outer)
        reg_l0 = 0.2
        reg_l1 = 0.1
        reg_l2 = 1e-4
        nu = 1e5
        old_reg_l0 = reg_l0
        old_ATA_scale = pm_opt.ATA_scale
        reg_l0, reg_l1, reg_l2, nu = rescale_for_opt(pm_opt, reg_l0, reg_l1, reg_l2, nu)
        assert np.isclose(reg_l0, old_reg_l0 / (2 * nu))
        assert np.isclose(pm_opt.ATA_scale, old_ATA_scale + 2 * reg_l2 + 1.0 / nu)
        reg_l0 = -1
        with self.assertRaises(ValueError):
            reg_l0, reg_l1, reg_l2, nu = rescale_for_opt(pm_opt, reg_l0, reg_l1, reg_l2, nu)
        reg_l0 = 2
        with self.assertRaises(ValueError):
            reg_l0, reg_l1, reg_l2, nu = rescale_for_opt(pm_opt, reg_l0, reg_l1, reg_l2, nu)

        # Test write PermanentMagnetGrid to FAMUS file
        write_pm_optimizer_to_famus('', pm_opt)
        pm_opt.coordinate_flag = 'cylindrical'
        write_pm_optimizer_to_famus('', pm_opt)
        pm_opt.coordinate_flag = 'toroidal'
        write_pm_optimizer_to_famus('', pm_opt)

        # Load in file we made to FocusData class and do some tests
        mag_data = FocusData('SIMSOPT_dipole_solution.focus')
        for i in range(mag_data.nMagnets):
            assert np.isclose(np.dot(np.array(mag_data.perp_vector([i])).T, np.array(mag_data.unit_vector([i]))), 0.0)
        mag_data.print_to_file('test')
        mag_data.init_pol_vecs(3)
        assert mag_data.pol_x.shape == (mag_data.nMagnets, 3)
        assert mag_data.pol_y.shape == (mag_data.nMagnets, 3)
        assert mag_data.pol_z.shape == (mag_data.nMagnets, 3)
        nMagnets = mag_data.nMagnets
        mag_data.repeat_hp_to_fp(nfp=2, magnet_sector=1)
        assert mag_data.nMagnets == nMagnets * 2
        assert np.allclose(mag_data.oz[:mag_data.nMagnets // 2], -mag_data.oz[mag_data.nMagnets // 2:])

        # Test algorithm kwarg initialization
        kwargs = initialize_default_kwargs(algorithm='RS')
        assert isinstance(kwargs, dict)
        kwargs = initialize_default_kwargs(algorithm='GPMO')
        assert isinstance(kwargs, dict)
        kwargs = initialize_default_kwargs(algorithm='ArbVec_backtracking')
        kwargs['verbose'] = False
        assert isinstance(kwargs, dict)
        assert kwargs['K'] == 1000

        # Test Bnormal plots
        make_Bnormal_plots(bs, s, '', 'biot_savart_test')

        # optimize pm_opt and plot optimization progress
        kwargs = initialize_default_kwargs(algorithm='GPMO')
        kwargs['K'] = 100
        kwargs['nhistory'] = 10
        kwargs['verbose'] = False
        R2_history, Bn_history, m_history = GPMO(pm_opt, 'baseline', **kwargs)
        m_history = np.transpose(m_history, [2, 0, 1])
        m_history = m_history.reshape(1, 11, 252, 3)
        make_optimization_plots(R2_history, m_history, m_history, pm_opt, '')

        pm_opt.geo_setup_from_famus(TEST_DIR / 'zot80.focus')
        R2_history, Bn_history, m_history = GPMO(pm_opt, 'baseline', **kwargs)
        make_optimization_plots(R2_history, m_history, m_history, pm_opt, '')
        kwargs['K'] = 5
        with self.assertRaises(ValueError):
            R2_history, Bn_history, m_history = GPMO(pm_opt, 'baseline', **kwargs)

    def test_pm_high_res(self):
        """
            Test the functions like QFM and poincare cross sections that
            can be only run with high resolution solutions.
        """

        # Test build of the MUSE coils
        input_name = 'input.muse'
        nphi = 8
        ntheta = nphi
        surface_filename = TEST_DIR / input_name
        s = SurfaceRZFourier.from_focus(surface_filename, range="half period", nphi=nphi, ntheta=ntheta)
        base_curves, curves, coils = initialize_coils('muse_famus', TEST_DIR, '', s)
        bs = BiotSavart(coils)
        B0avg = calculate_on_axis_B(bs, s)
        assert np.allclose(B0avg, 0.15)

        pm_opt = PermanentMagnetGrid(
            s,
            Bn=np.zeros(s.normal().shape[:2]), 
        )
        pm_opt.geo_setup_from_famus(TEST_DIR / 'zot80.focus')
        kwargs = initialize_default_kwargs(algorithm='GPMO')
        kwargs['verbose'] = False
        kwargs['K'] = 15000
        R2_history, Bn_history, m_history = GPMO(pm_opt, 'baseline', **kwargs)
        b_dipole = DipoleField(
            pm_opt.dipole_grid_xyz,
            pm_opt.m, 
            nfp=s.nfp,
            coordinate_flag=pm_opt.coordinate_flag,
            m_maxima=pm_opt.m_maxima,
        )
        # Make higher resolution surface for qfm
        qphi = 2 * nphi
        quadpoints_phi = np.linspace(0, 1, qphi, endpoint=True)
        quadpoints_theta = np.linspace(0, 1, ntheta, endpoint=True)
        s_plot = SurfaceRZFourier.from_focus(
            surface_filename, range="full torus",
            quadpoints_phi=quadpoints_phi, quadpoints_theta=quadpoints_theta
        )
        comm = None 

        # Make QFM surfaces
        Bfield = bs + b_dipole
        Bfield.set_points(s_plot.gamma().reshape((-1, 3)))
        qfm_surf = make_qfm(s_plot, Bfield)
        qfm_surf = qfm_surf.surface

        # Run poincare plotting
        run_Poincare_plots(s_plot, bs, b_dipole, comm, 'poincare_test', '')


if __name__ == "__main__":
    unittest.main()
