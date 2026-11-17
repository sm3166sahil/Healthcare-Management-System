"""
NumPy Healthcare Data Analysis Engine
FDS Unit 1 Coverage: Array Creation, Indexing, Slicing, Reshaping,
Universal Functions, Mathematical Ops, Random Distributions, Linear Algebra.
"""

import numpy as np


class HealthcareNumpyAnalyzer:
    """
    Dedicated NumPy computational engine demonstrating Unit 1 syllabus concepts
    with rigorous healthcare domain examples.
    """

    def __init__(self, data=None):
        if data is not None:
            self.data = np.asarray(data, dtype=float)
        else:
            # Standard physiological baseline: heart rates (bpm)
            np.random.seed(42)
            self.data = np.random.normal(loc=75.0, scale=12.0, size=100)

    # ---------------------------------------------------------
    # A. ARRAY CREATION & PROPERTIES (FDS Unit 1)
    # ---------------------------------------------------------
    @staticmethod
    def demonstrate_array_creation():
        """Demonstrates diverse NumPy array initialization methods."""
        results = {}
        # 1. Direct array creation
        arr_1d = np.array([72, 85, 90, 68, 74, 110, 65, 80])
        results['np_array_1d'] = {
            'array': arr_1d.tolist(),
            'shape': arr_1d.shape,
            'ndim': arr_1d.ndim,
            'size': int(arr_1d.size),
            'dtype': str(arr_1d.dtype)
        }

        # 2. Zeros, Ones, Full
        zeros_arr = np.zeros((3, 4), dtype=int)
        ones_arr = np.ones((2, 3), dtype=float)
        full_arr = np.full((2, 2), 98.6)  # Baseline body temperature

        results['zeros'] = zeros_arr.tolist()
        results['ones'] = ones_arr.tolist()
        results['full_temp'] = full_arr.tolist()

        # 3. Arange and Linspace
        # Dosage ranges: 10mg to 100mg with step 10
        dosage_range = np.arange(10, 110, 10)
        # Continuous titration concentrations: 0.1 to 1.0 with 5 equidistant points
        titration_points = np.linspace(0.1, 1.0, 5)

        results['arange_dosage'] = dosage_range.tolist()
        results['linspace_titration'] = np.round(titration_points, 3).tolist()

        # 4. Identity and Eye matrices (transition & projection kernels)
        eye_mat = np.eye(3)
        results['eye_matrix'] = eye_mat.tolist()

        return results

    # ---------------------------------------------------------
    # B. ARRAY MANIPULATION & SLICING (FDS Unit 1)
    # ---------------------------------------------------------
    @staticmethod
    def demonstrate_manipulation():
        """Demonstrates reshaping, slicing, flattening, and joining."""
        # 12 patient systolic BP measurements over 3 shifts (Morning, Afternoon, Night)
        bp_data = np.array([120, 122, 118, 130, 125, 128, 135, 140, 138, 142, 145, 150])

        # Reshape to 3 shifts x 4 patients
        bp_matrix = bp_data.reshape((3, 4))

        # Slicing: Patient 1 & 2 in shifts 1 & 2
        sliced = bp_matrix[0:2, 0:2]

        # Flattening
        flattened = bp_matrix.flatten()

        # Splitting
        shift1, shift2, shift3 = np.split(bp_matrix, 3, axis=0)

        # Stacking / Joining
        stacked = np.vstack([shift1, shift2])

        return {
            'original_shape': bp_data.shape,
            'reshaped_3x4': bp_matrix.tolist(),
            'sliced_2x2': sliced.tolist(),
            'flattened': flattened.tolist(),
            'split_shifts': [s.tolist() for s in [shift1, shift2, shift3]],
            'vertically_stacked': stacked.tolist()
        }

    # ---------------------------------------------------------
    # C. MATHEMATICAL OPERATIONS & BROADCASTING
    # ---------------------------------------------------------
    @staticmethod
    def demonstrate_math_broadcasting():
        """Demonstrates universal functions, vectorization, and broadcasting."""
        systolic = np.array([120.0, 135.0, 142.0, 118.0, 155.0])
        diastolic = np.array([80.0, 88.0, 92.0, 78.0, 98.0])

        # Vectorized pulse pressure calculation: Systolic - Diastolic
        pulse_pressure = systolic - diastolic

        # Mean Arterial Pressure (MAP) = Diastolic + (1/3 * Pulse Pressure)
        map_values = diastolic + (pulse_pressure / 3.0)

        # Broadcasting: Apply altitude adjustment (+5.0 mmHg)
        altitude_adjusted = systolic + 5.0

        # Universal functions: log transform, square root, exponential
        biomarker = np.array([1.2, 3.4, 0.8, 12.5, 45.2])
        log_biomarker = np.log(biomarker)
        sqrt_biomarker = np.sqrt(biomarker)

        bp_table = [
            {
                'systolic': float(systolic[i]),
                'diastolic': float(diastolic[i]),
                'pulse_pressure': float(pulse_pressure[i]),
                'mean_arterial_pressure': float(round(map_values[i], 2)),
            }
            for i in range(len(systolic))
        ]

        return {
            'systolic': systolic.tolist(),
            'diastolic': diastolic.tolist(),
            'pulse_pressure': pulse_pressure.tolist(),
            'mean_arterial_pressure': np.round(map_values, 2).tolist(),
            'broadcasting_adjusted': altitude_adjusted.tolist(),
            'log_transformed': np.round(log_biomarker, 4).tolist(),
            'sqrt_transformed': np.round(sqrt_biomarker, 4).tolist(),
            'bp_table': bp_table,
        }

    # ---------------------------------------------------------
    # D. STATISTICAL OPERATIONS (FDS Unit 1)
    # ---------------------------------------------------------
    def compute_statistics(self):
        """Computes comprehensive descriptive statistics on the loaded array."""
        clean_data = self.data[~np.isnan(self.data)]
        if len(clean_data) == 0:
            return {}

        return {
            'count': int(clean_data.size),
            'mean': float(np.mean(clean_data)),
            'std_dev': float(np.std(clean_data)),
            'variance': float(np.var(clean_data)),
            'min': float(np.min(clean_data)),
            'max': float(np.max(clean_data)),
            'median': float(np.median(clean_data)),
            'q1_25th': float(np.percentile(clean_data, 25)),
            'q3_75th': float(np.percentile(clean_data, 75)),
            'iqr': float(np.percentile(clean_data, 75) - np.percentile(clean_data, 25)),
            '95th_percentile': float(np.percentile(clean_data, 95)),
            '99th_percentile': float(np.percentile(clean_data, 99)),
        }

    # ---------------------------------------------------------
    # E. RANDOM DISTRIBUTIONS (FDS Unit 1)
    # ---------------------------------------------------------
    @staticmethod
    def generate_random_distributions(size=200):
        """Demonstrates Unit 1 random distribution generators."""
        np.random.seed(42)
        distributions = {
            'normal_heart_rate': np.random.normal(loc=72, scale=10, size=size),
            'uniform_age': np.random.uniform(low=18, high=85, size=size),
            'binomial_positive_outcome': np.random.binomial(n=1, p=0.25, size=size),
            'poisson_emergency_admissions': np.random.poisson(lam=4.5, size=size),
            'exponential_survival_time': np.random.exponential(scale=30.0, size=size),
            'chisquare_variance_test': np.random.chisquare(df=4, size=size)
        }

        summary = {}
        for name, arr in distributions.items():
            summary[name] = {
                'mean': float(np.mean(arr)),
                'std': float(np.std(arr)),
                'min': float(np.min(arr)),
                'max': float(np.max(arr)),
                'sample': np.round(arr[:5], 3).tolist()
            }
        return summary

    # ---------------------------------------------------------
    # F. LINEAR ALGEBRA (FDS Unit 1)
    # ---------------------------------------------------------
    @staticmethod
    def demonstrate_linear_algebra():
        """Demonstrates matrix multiplication, determinants, inverses, and eigenvalues."""
        # Covariance / Transition Matrix between 3 biomarkers: [Glucose, Cholesterol, BP]
        A = np.array([
            [4.0, 1.2, 0.8],
            [1.2, 3.5, 0.5],
            [0.8, 0.5, 2.8]
        ])

        # Weights vector for clinical cardiovascular risk score
        weights = np.array([0.4, 0.35, 0.25])

        # Matrix-vector multiplication
        risk_projection = np.dot(A, weights)

        # Transpose
        A_transpose = A.T

        # Determinant
        det_A = float(np.linalg.det(A))

        # Matrix Inverse
        inv_A = np.linalg.inv(A)

        # Eigenvalues and Eigenvectors (Principal component axes)
        eigenvalues, eigenvectors = np.linalg.eig(A)

        return {
            'matrix_A': A.tolist(),
            'weights': weights.tolist(),
            'dot_product_risk': np.round(risk_projection, 3).tolist(),
            'transpose': A_transpose.tolist(),
            'determinant': round(det_A, 4),
            'inverse': np.round(inv_A, 4).tolist(),
            'eigenvalues': np.round(eigenvalues, 4).tolist(),
            'eigenvectors': np.round(eigenvectors, 4).tolist()
        }
