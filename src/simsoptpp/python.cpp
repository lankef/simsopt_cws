#include "pybind11/pybind11.h"
#include "pybind11/stl.h"
#include "pybind11/functional.h"
#define FORCE_IMPORT_ARRAY
#include "xtensor-python/pyarray.hpp"     // Numpy bindings
#include <Eigen/Core>
typedef xt::pyarray<double> PyArray;
#include <math.h>
#include <chrono>




#include "biot_savart_py.h"
#include "biot_savart_vjp_py.h"
#include "dommaschk.h"
#include "reiman.h"
#include "boozerradialinterpolant.h"

namespace py = pybind11;

using std::vector;
using std::shared_ptr;

void init_surfaces(py::module_ &);
void init_curves(py::module_ &);
void init_magneticfields(py::module_ &);
void init_boozermagneticfields(py::module_ &);
void init_tracing(py::module_ &);

template<class T>
bool empty_intersection(const std::set<T>& x, const std::set<T>& y)
{
    auto i = x.begin();
    auto j = y.begin();
    while (i != x.end() && j != y.end())
    {
        if (*i == *j)
            return false;
        else if (*i < *j)
            ++i;
        else
            ++j;
    }
    return true;
}

bool two_points_too_close_exist(PyArray& XA, PyArray& XB, double threshold_squared){
    for (int k = 0; k < XA.shape(0); ++k) {
        for (int l = 0; l < XB.shape(0); ++l) {
            double dist = std::pow(XA(k, 0) - XB(l, 0), 2) + std::pow(XA(k, 1) - XB(l, 1), 2) + std::pow(XA(k, 2) - XB(l, 2), 2);
            if(dist < threshold_squared)
                return true;
        }
    }
    return false;
}


PYBIND11_MODULE(simsoptpp, m) {
    xt::import_numpy();

    init_curves(m);
    init_surfaces(m);
    init_magneticfields(m);
    init_boozermagneticfields(m);
    init_tracing(m);

    m.def("biot_savart", &biot_savart);
    m.def("biot_savart_B", &biot_savart_B);
    m.def("biot_savart_vjp", &biot_savart_vjp);
    m.def("biot_savart_vjp_graph", &biot_savart_vjp_graph);
    m.def("biot_savart_vector_potential_vjp_graph", &biot_savart_vector_potential_vjp_graph);

    m.def("DommaschkB" , &DommaschkB);
    m.def("DommaschkdB", &DommaschkdB);

    m.def("ReimanB" , &ReimanB);
    m.def("ReimandB", &ReimandB);

    m.def("fourier_transform_even", &fourier_transform_even);
    m.def("fourier_transform_odd", &fourier_transform_odd);
    m.def("inverse_fourier_transform_even", &inverse_fourier_transform_even);
    m.def("inverse_fourier_transform_odd", &inverse_fourier_transform_odd);
    m.def("compute_kmns",&compute_kmns);

    // the computation below is used in boozer_surface_residual.
    //
    // G*dB_dc - 2*np.sum(B[..., None]*dB_dc, axis=2)[:, :, None, :] * tang[..., None] - B2[..., None, None] * (dxphi_dc + iota * dxtheta_dc)
    m.def("boozer_dresidual_dc", [](double G, PyArray& dB_dc, PyArray& B, PyArray& tang, PyArray& B2, PyArray& dxphi_dc, double iota, PyArray& dxtheta_dc) {
            int nphi = dB_dc.shape(0);
            int ntheta = dB_dc.shape(1);
            int ndofs = dB_dc.shape(3);
            PyArray res = xt::zeros<double>({nphi, ntheta, 3, ndofs});
            double* B_dB_dc = new double[ndofs];
            for(int i=0; i<nphi; i++){
                for(int j=0; j<ntheta; j++){
                    for (int m = 0; m < ndofs; ++m) {
                        B_dB_dc[m] = B(i, j, 0)*dB_dc(i, j, 0, m) + B(i, j, 1)*dB_dc(i, j, 1, m) + B(i, j, 2)*dB_dc(i, j, 2, m);
                    }
                    double B2ij = B2(i, j);
                    for (int d = 0; d < 3; ++d) {
                        auto dB_dc_ptr = &(dB_dc(i, j, d, 0));
                        auto res_ptr = &(res(i, j, d, 0));
                        auto dxphi_dc_ptr = &(dxphi_dc(i, j, d, 0));
                        auto dxtheta_dc_ptr = &(dxtheta_dc(i, j, d, 0));
                        auto tangijd = tang(i, j, d);
                        for (int m = 0; m < ndofs; ++m) {
                            res_ptr[m] = G*dB_dc_ptr[m]
                            - 2*B_dB_dc[m]*tangijd
                            - B2ij * (dxphi_dc_ptr[m] + iota*dxtheta_dc_ptr[m]);
                        }
                    }
                }
            }
            delete[] B_dB_dc;
            return res;
        });

    m.def("matmult", [](PyArray& A, PyArray&B) {
            // Product of an lxm matrix with an mxn matrix, results in an l x n matrix
            int l = A.shape(0);
            int m = A.shape(1);
            int n = B.shape(1);
            PyArray C = xt::zeros<double>({l, n});

            Eigen::Map<Eigen::Matrix<double,Eigen::Dynamic,Eigen::Dynamic,Eigen::RowMajor>> eigA(const_cast<double*>(A.data()), l, m);
            Eigen::Map<Eigen::Matrix<double,Eigen::Dynamic,Eigen::Dynamic,Eigen::RowMajor>> eigB(const_cast<double*>(B.data()), m, n);
            Eigen::Map<Eigen::Matrix<double,Eigen::Dynamic,Eigen::Dynamic,Eigen::RowMajor>> eigC(const_cast<double*>(C.data()), l, n);
            eigC = eigA*eigB;
            return C;
        });

    m.def("vjp", [](PyArray& v, PyArray&B) {
            // Product of v.T @ B
            int m = B.shape(0);
            int n = B.shape(1);
            PyArray C = xt::zeros<double>({n});

            Eigen::Map<Eigen::Matrix<double,Eigen::Dynamic,Eigen::Dynamic,Eigen::RowMajor>> eigv(const_cast<double*>(v.data()), m, 1);
            Eigen::Map<Eigen::Matrix<double,Eigen::Dynamic,Eigen::Dynamic,Eigen::RowMajor>> eigB(const_cast<double*>(B.data()), m, n);
            Eigen::Map<Eigen::Matrix<double,Eigen::Dynamic,Eigen::Dynamic,Eigen::RowMajor>> eigC(const_cast<double*>(C.data()), 1, n);
            eigC = eigv.transpose()*eigB;
            return C;
        });

    using std::chrono::high_resolution_clock;
    using std::chrono::duration_cast;
    using std::chrono::duration;
    using std::chrono::nanoseconds;

    m.def("get_close_candidates", [](std::vector<PyArray>& pointClouds, double threshold, int num_base_curves) {
        /*
        Returns all pairings of the given pointClouds that have two points that
        are less than `threshold` away. The estimate is approximate (for
        speed), so this function may return too many (but not too few!)
        pairings.

        The basic idea of this function is the following:
        - Assume we want to compare pointcloud A and B.
        - We create a uniform grid of cell size threshold.
        - Loop over points in cloud A, mark all cells that have a point in it (via the `set` variables below).
        - Loop over points in cloud B, mark all cells that have a point in it and also all cells in the 8 neighbouring cells around it.
        - Check whether the intersection between the two sets is non-empty.
        */
        std::vector<std::set<std::tuple<int, int, int>>> sets(pointClouds.size());
        std::vector<std::set<std::tuple<int, int, int>>> sets_extended(pointClouds.size());
#pragma omp parallel for
        for (int p = 0; p < pointClouds.size(); ++p) {
            std::set<std::tuple<int, int, int>> s;
            std::set<std::tuple<int, int, int>> s_extended;
            PyArray& points = pointClouds[p];
            for (int l = 0; l < points.shape(0); ++l) {
                int i = std::floor(points(l, 0)/threshold);
                int j = std::floor(points(l, 1)/threshold);
                int k = std::floor(points(l, 2)/threshold);
                sets[p].insert({i, j, k});
                for (int ii = -1; ii <= 1; ++ii) {
                    for (int jj = -1; jj <= 1; ++jj) {
                        for (int kk = -1; kk <= 1; ++kk) {
                            sets_extended[p].insert({i + ii, j + jj, k + kk});
                        }
                    }
                }
            }
        }


        std::vector<std::tuple<int, int>> candidates_1;
        for (int i = 0; i < pointClouds.size(); ++i) {
            for (int j = 0; j < i; ++j) {
                if(j < num_base_curves)
                    candidates_1.push_back({i, j});
            }
        }
        std::vector<std::tuple<int, int>> candidates_2;
#pragma omp parallel for
        for (int k = 0; k < candidates_1.size(); ++k) {
            int i = std::get<0>(candidates_1[k]);
            int j = std::get<1>(candidates_1[k]);
            bool check = empty_intersection(sets_extended[i], sets[j]);
#pragma omp critical
            if(!check)
                candidates_2.push_back({i, j});
        }

        double t2 = threshold*threshold;
        std::vector<std::tuple<int, int>> candidates_3;
#pragma omp parallel for
        for (int k = 0; k < candidates_2.size(); ++k) {
            int i = std::get<0>(candidates_2[k]);
            int j = std::get<1>(candidates_2[k]);
            bool check = two_points_too_close_exist(pointClouds[i], pointClouds[j], t2);
#pragma omp critical
            if(check)
                candidates_3.push_back({i, j});
        }
        return candidates_3;
    }, "Get candidates for which point clouds are closer than threshold to each other.", py::arg("pointClouds"), py::arg("threshold"), py::arg("num_base_curves"));

#ifdef VERSION_INFO
    m.attr("__version__") = VERSION_INFO;
#else
    m.attr("__version__") = "dev";
#endif
}
