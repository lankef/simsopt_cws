from .._core.optimizable import DOFs, Optimizable
import logging

import numpy as np

logger = logging.getLogger(__name__)

try:
    import py_spec
except ImportError as e:
    py_spec = None
    logger.debug(str(e))


__all__ = ['NormalField']


class NormalField(Optimizable):
    r"""
    ``NormalField`` represents the normal field on a boundary, for example the
    computational boundary of SPEC free-boundary.

    Args:
        nfp: The number of field period
        stellsym: Whether (=True) or not (=False) stellarator symmetry is enforced.
        mpol: Poloidal Fourier resolution
        ntor: Toroidal Fourier resolution
        vns: Odd fourier modes of :math: `\mathbf{B}\cdot\mathbf{\hat{n}}`. 2D array of size
          (mpol+1)x(2ntor+1). Set to None to fill with zeros
        vnc: Even fourier modes of :math: `\mathbf{B}\cdot\mathbf{\hat{n}}`. 2D array of size
          (mpol+1)x(2ntor+1). Ignored if stellsym if True. Set to None to fill with zeros
    """

    def __init__(self, nfp=1, stellsym=True, mpol=1, ntor=0,
                 vns=None, vnc=None):

        self.nfp = nfp
        self.stellsym = stellsym
        self.mpol = mpol
        self.ntor = ntor

        if vns is None:
            self.vns = np.zeros((self.mpol + 1, 2 * self.ntor + 1))
        else:
            self.vns = vns[0:self.mpol + 1,0:2*self.ntor+1]

        if self.stellsym:
            self.ndof = self.ntor + self.mpol * (2 * self.ntor + 1)
            self.vnc = np.array(())
        else:
            self.ndof = 2 * (self.ntor + self.mpol * (2 * self.ntor + 1)) + 1
            if vnc is None:
                self.vnc = np.zeros((self.mpol + 1, 2 * self.ntor + 1))
            else:
                self.vnc = vnc[0:self.mpol + 1,0:2*self.ntor+1]

        Optimizable.__init__(
            self,
            x0=self.get_dofs(),
            names=self._make_names())

    @classmethod
    def init_from_spec(cls, filename):
        """
        Initialize using the harmonics in SPEC input file
        """

        # Test if py_spec is available
        if py_spec is None:
            raise RuntimeError(
                "Initialization from Spec requires py_spec to be installed.")

        # Read Namelist
        nm = py_spec.SPECNamelist(filename)
        ph = nm['physicslist']

        nf = cls(nfp=ph['nfp'], stellsym=ph['istellsym'], mpol=ph['Mpol'], ntor=ph['Ntor'])

        if nf.stellsym:
            nf.ndof = nf.ntor + nf.mpol * \
                (2 * nf.ntor + 1)  # Only Vns - odd series
        else:
            nf.ndof = 2 * (nf.ntor + nf.mpol *
                             (2 * nf.ntor + 1)) + 1  # Vns and Vnc

        nf.vns = np.zeros((nf.mpol + 1, 2 * nf.ntor + 1))

        vns = np.asarray(ph['vns'])
        if not nf.stellsym:
            vnc = np.asarray(ph['vnc'][1:])
            nf.vnc = np.zeros((nf.mpol + 1, 2 * nf.ntor + 1))

        mntor = int((vns.shape[1] - 1) / 2.0)

        for mm in range(0, nf.mpol + 1):
            for nn in range(-nf.ntor, nf.ntor + 1):
                if mm == 0 and nn < 0:
                    continue
                nf.set_vns(mm, nn, vns[mm,mntor + nn])

                if not nf.stellsym:
                    nf.set_vnc(mm, nn, vnc[mm,mntor + nn])

        return nf

    def get_dofs(self):
        """
        Return the dofs associated to this normal field as an array.
        """

        nvn = self.vns.size
        dofs = np.reshape( self.vns, nvn )
        dofs = dofs[self.ntor+1:] # remove m=0, n<=0 harmonics

        if not self.stellsym:
            dofs_vnc = np.reshape( self.vnc, nvn )
            dofs_vnc = dofs_vnc[self.ntor:] # remove m=0, n<0 harmonics

            dofs = np.append(dofs, dofs_vnc)

        return dofs

    def set_dofs(self, dofs):
        """
        Set the vnc, vns from an array
        """
        if not dofs.size == self.ndof:
            raise ValueError('Invalid number of dofs')

        nvns = self.ntor + self.mpol * (self.ntor * 2 + 1)
        vns_dofs = np.append( np.zeros(self.ntor+1), dofs[:nvns]) 
        self.vns = np.reshape( vns_dofs, (self.mpol+1,2*self.ntor+1) )

        if not self.stellsym:
            vnc_dofs = np.append( np.zeros(self.ntor) , dofs[nvns:] )
            self.vnc = np.reshape(vnc_dofs, (self.mpol+1, 2*self.ntor+1) )

        


    def get_index_in_dofs(self, m, n, even=False):
        """
        Returns position of mode (m,n) in dofs array
        """

        self.check_mn(m, n)

        ii = -1

        if m == 0:
            ii = m - 1
        else:
            ii = self.ntor + 1 + (2 * self.ntor + 1) * \
                (m - 1) + n + self.ntor + 1 - 1

        nvns = self.ntor + self.mpol * (self.ntor * 2 + 1)
        if not even:  # Vns
            ii = ii - 1  # remove (0,0) element
        else:  # Vnc
            ii = ii + nvns

        return ii

    def get_vns(self, m, n):
        self.check_mn(m, n)
        return self.vns[m,n+self.ntor]

    def set_vns(self, m, n, value):
        self.check_mn(m, n)
        self.vns[m,n+self.ntor] = value

    def get_vnc(self, m, n):
        self.check_mn(m, n)
        if self.stellsym:
            return 0.0
        else:
            return self.vnc[m,n+self.ntor]

    def set_vnc(self, m, n, value):
        self.check_mn(m, n)
        if self.stellsym:
            raise ValueError('Stellarator symmetric has no vnc')
        else:
            self.vnc[m,n+self.ntor] = value

    def check_mn(self, m, n):
        if m < 0 or m > self.mpol:
            raise ValueError('m out of bound')
        if n < -self.ntor or n > self.ntor:
            raise ValueError('n out of bound')
        if m == 0 and n < 0:
            raise ValueError('n has to be positive if m==0')

    def _make_names(self):
        """
        Form a list of names of the ``rc``, ``zs``, ``rs``, or ``zc``
        array elements.  The order of these four arrays here must
        match the order in ``set_dofs_impl()`` and ``get_dofs()`` in
        ``src/simsoptpp/surfacerzfourier.h``.
        """
        if self.stellsym:
            names = self._make_names_helper('vns', False)
        else:
            names = self._make_names_helper('vnc', True) \
                + self._make_names_helper('vns', False)

        return names

    def _make_names_helper(self, prefix, include0):
        if include0:
            names = [prefix + "(0,0)"]
        else:
            names = []

        names += [prefix +
                  '(0,' + str(n) + ')' for n in range(1, self.ntor + 1)]
        for m in range(1, self.mpol + 1):
            names += [prefix + '(' + str(m) + ',' + str(n) +
                      ')' for n in range(-self.ntor, self.ntor + 1)]
        return names

    def change_resolution(self, mpol, ntor):
        """
        Change the values of `mpol` and `ntor`. Any new Fourier amplitudes
        will have a magnitude of zero.  Any previous nonzero Fourier
        amplitudes that are not within the new range will be
        discarded.
        """
        old_mpol = self.mpol
        old_ntor = self.ntor
        old_vns = self.vns
        if not self.stellsym:
            old_zc = self.vnc

        # Set new resolution
        self.mpol = mpol
        self.ntor = ntor

        # Set new number of dofs
        if self.stellsym:
            self.ndof = self.ntor + self.mpol * \
                (2 * self.ntor + 1)  # Only Vns - odd series
        else:
            self.ndof = 2 * (self.ntor + self.mpol *
                             (2 * self.ntor + 1)) + 1  # Vns and Vnc

        # Erase vns, vnc and fill with zeros
        self.vns = np.zeros((self.mpol + 1, 2 * self.ntor + 1))
        if not self.stellsym:
            self.vnc = np.zeros((self.mpol + 1, 2 * self.ntor + 1))

        # Fill relevant modes
        min_mpol = np.min((mpol, old_mpol))
        min_ntor = np.min((ntor, old_ntor))
        for m in range(min_mpol + 1):
            for n in range(-min_ntor, min_ntor + 1):
                self.vns[m,n+self.ntor] = old_vns[m,n+old_ntor]
                if not self.stellsym:
                    self.zc[m,n+self.ntor] = old_zc[m,n+old_ntor]

        # Update the dofs object
        self._dofs = DOFs(self.get_dofs(), self._make_names())

        # The following methods of graph Optimizable framework need to be
        # called
        Optimizable._update_free_dof_size_indices(self)
        Optimizable._update_full_dof_size_indices(self)
        Optimizable._set_new_x(self)

    def fixed_range(self, mmin, mmax, nmin, nmax, fixed=True):
        """
        Set the 'fixed' property for a range of `m` and `n` values.

        All modes with `m` in the interval [`mmin`, `mmax`] and `n` in the
        interval [`nmin`, `nmax`] will have their fixed property set to
        the value of the `fixed` parameter. Note that `mmax` and `nmax`
        are included (unlike the upper bound in python's range(min,
        max).)
        """

        fn = self.fix if fixed else self.unfix
        for m in range(mmin, mmax + 1):
            this_nmin = nmin
            if m == 0 and nmin < 0:
                this_nmin = 0
            for n in range(this_nmin, nmax + 1):
                if m > 0 or n != 0:
                    fn(f'vns({m},{n})')
                if not self.stellsym:
                    fn(f'vnc({m},{n})')
