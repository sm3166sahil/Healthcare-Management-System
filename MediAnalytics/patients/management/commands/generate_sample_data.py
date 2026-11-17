"""
MediAnalytics - Sample Synthetic Healthcare Data Generation Management Command
Generates reproducible synthetic patient and clinical datasets for FDS demonstration.
"""

import os
import random
from datetime import date, timedelta
import numpy as np
import pandas as pd

from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone


class Command(BaseCommand):
    help = 'Generates synthetic patients, medical records, and CSV dataset for MediAnalytics'

    def add_arguments(self, parser):
        parser.add_argument(
            '--patients',
            type=int,
            default=500,
            help='Number of synthetic patients to generate (default: 500)'
        )
        parser.add_argument(
            '--records',
            type=int,
            default=1100,
            help='Number of medical records to generate (default: 1100)'
        )
        parser.add_argument(
            '--csv-rows',
            type=int,
            default=500,
            help='Number of rows for the CSV dataset (default: 500)'
        )

    def handle(self, *args, **options):
        # Set seeds for complete reproducibility
        np.random.seed(42)
        random.seed(42)

        self.stdout.write(self.style.NOTICE('================================================================='))
        self.stdout.write(self.style.NOTICE(' MediAnalytics: Generating Synthetic Healthcare Demonstration Data '))
        self.stdout.write(self.style.NOTICE('================================================================='))

        # 1. Superuser Creation
        admin_user = self.create_admin_user()

        # 2. Generate Patient Records in Database
        num_patients = options['patients']
        patients_list = self.generate_patients(num_patients, admin_user)

        # 3. Generate Medical Records in Database
        num_records = options['records']
        self.generate_medical_records(patients_list, num_records, admin_user)

        # 4. Generate Synthetic CSV Dataset with Controlled Anomalies
        csv_rows = options['csv_rows']
        csv_path = self.generate_csv_dataset(csv_rows)

        # 5. Register Dataset in UploadedDataset Model
        self.register_uploaded_dataset(csv_path, admin_user, csv_rows)

        self.stdout.write(self.style.SUCCESS('\nSynthetic data generation completed successfully!'))

    def create_admin_user(self):
        """Creates default administrative account if not already existing."""
        User = get_user_model()
        try:
            admin, created = User.objects.get_or_create(
                username='admin',
                defaults={
                    'email': 'admin@example.com',
                    'is_staff': True,
                    'is_superuser': True
                }
            )
            if created:
                admin.set_password('admin123')
                # Check for custom role field if present
                if hasattr(admin, 'role'):
                    admin.role = 'Admin'
                admin.save()
                self.stdout.write(self.style.SUCCESS('Created default superuser: admin (password: admin123)'))
            else:
                self.stdout.write(self.style.SUCCESS('Default superuser "admin" already exists.'))
            return admin
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Note on admin user: {str(e)}'))
            return User.objects.first()

    def generate_patients(self, count, admin_user):
        """Generates synthetic patients with realistic demographic data."""
        self.stdout.write(f'\nCreating {count} synthetic patient records in database...')

        first_names_male = [
            'James', 'John', 'Robert', 'Michael', 'William', 'David', 'Richard', 'Joseph',
            'Thomas', 'Charles', 'Daniel', 'Matthew', 'Anthony', 'Donald', 'Mark', 'Paul',
            'Steven', 'Andrew', 'Kenneth', 'Joshua', 'Kevin', 'Brian', 'George', 'Edward',
            'Ronald', 'Timothy', 'Jason', 'Jeffrey', 'Ryan', 'Jacob', 'Gary', 'Nicholas',
            'Eric', 'Jonathan', 'Stephen', 'Larry', 'Justin', 'Scott', 'Brandon', 'Benjamin',
            'Samuel', 'Gregory', 'Alexander', 'Frank', 'Patrick', 'Raymond', 'Jack', 'Dennis',
            'Jerry', 'Tyler', 'Aaron', 'Jose', 'Adam', 'Nathan', 'Henry', 'Douglas', 'Zachary',
            'Peter', 'Kyle', 'Walter', 'Ethan', 'Jeremy', 'Harold', 'Keith', 'Christian', 'Roger',
            'Noah', 'Gerald', 'Carl', 'Terry', 'Sean', 'Austin', 'Arthur', 'Lawrence', 'Jesse'
        ]

        first_names_female = [
            'Mary', 'Patricia', 'Jennifer', 'Linda', 'Elizabeth', 'Barbara', 'Susan', 'Jessica',
            'Sarah', 'Karen', 'Nancy', 'Lisa', 'Betty', 'Margaret', 'Sandra', 'Ashley',
            'Kimberly', 'Emily', 'Donna', 'Michelle', 'Dorothy', 'Carol', 'Amanda', 'Melissa',
            'Deborah', 'Stephanie', 'Rebecca', 'Sharon', 'Laura', 'Cynthia', 'Kathleen', 'Amy',
            'Shirley', 'Angela', 'Helen', 'Anna', 'Brenda', 'Pamela', 'Nicole', 'Emma',
            'Samantha', 'Katherine', 'Christine', 'Debra', 'Rachel', 'Catherine', 'Carolyn', 'Janet',
            'Ruth', 'Maria', 'Heather', 'Diane', 'Virginia', 'Julie', 'Joyce', 'Victoria', 'Olivia',
            'Kelly', 'Christina', 'Lauren', 'Joan', 'Evelyn', 'Judith', 'Megan', 'Cheryl', 'Andrea',
            'Hannah', 'Martha', 'Jacqueline', 'Frances', 'Ann', 'Gloria', 'Jean', 'Kathryn', 'Alice'
        ]

        last_names = [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
            'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson',
            'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson',
            'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson', 'Walker',
            'Young', 'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores',
            'Green', 'Adams', 'Nelson', 'Baker', 'Hall', 'Rivera', 'Campbell', 'Mitchell',
            'Carter', 'Roberts', 'Gomez', 'Phillips', 'Evans', 'Turner', 'Diaz', 'Parker',
            'Cruz', 'Edwards', 'Collins', 'Reyes', 'Stewart', 'Morris', 'Morales', 'Murphy',
            'Cook', 'Rogers', 'Gutierrez', 'Ortiz', 'Morgan', 'Cooper', 'Peterson', 'Bailey',
            'Reed', 'Kelly', 'Howard', 'Ramos', 'Kim', 'Cox', 'Ward', 'Richardson', 'Watson'
        ]

        blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        cities = ['New York', 'Boston', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio', 'San Diego', 'Dallas']

        created_patients = []

        try:
            from patients.models import Patient
        except ImportError:
            self.stdout.write(self.style.WARNING('Could not import Patient model. Skipping database population.'))
            return []

        # Clear previous synthetic records if desired
        try:
            existing_count = Patient.objects.count()
            if existing_count > 0:
                self.stdout.write(f'Found {existing_count} existing patients. Adding additional records...')
        except Exception:
            pass

        patient_field_names = {f.name for f in Patient._meta.get_fields()}

        # Generate normal age distribution around 55, std 15, clipped 18 to 90
        ages = np.clip(np.random.normal(loc=55, scale=15, size=count).astype(int), 18, 90)

        for i in range(count):
            gender_raw = np.random.choice(['Male', 'Female'], p=[0.49, 0.51])
            if gender_raw == 'Male':
                fname = np.random.choice(first_names_male)
            else:
                fname = np.random.choice(first_names_female)
            lname = np.random.choice(last_names)
            age = int(ages[i])
            dob = date.today() - timedelta(days=int(age * 365.25) + int(np.random.randint(0, 360)))
            pat_code = f"SYN-PAT-{i+1:04d}"

            data = {}
            if 'patient_id' in patient_field_names:
                data['patient_id'] = pat_code
            if 'first_name' in patient_field_names:
                data['first_name'] = fname
            if 'last_name' in patient_field_names:
                data['last_name'] = lname
            if 'name' in patient_field_names:
                data['name'] = f"{fname} {lname}"
            if 'gender' in patient_field_names:
                data['gender'] = gender_raw
            if 'age' in patient_field_names:
                data['age'] = age
            if 'date_of_birth' in patient_field_names:
                data['date_of_birth'] = dob
            if 'dob' in patient_field_names:
                data['dob'] = dob
            if 'blood_group' in patient_field_names:
                data['blood_group'] = np.random.choice(blood_groups)
            if 'contact_number' in patient_field_names:
                data['contact_number'] = f"+1-555-{np.random.randint(100, 999)}-{np.random.randint(1000, 9999)}"
            if 'phone' in patient_field_names:
                data['phone'] = f"+1-555-{np.random.randint(100, 999)}-{np.random.randint(1000, 9999)}"
            if 'email' in patient_field_names:
                data['email'] = f"{fname.lower()}.{lname.lower()}{i+1}@example.com"
            if 'address' in patient_field_names:
                data['address'] = f"{np.random.randint(100, 9999)} Health Ave, {np.random.choice(cities)}"
            if 'emergency_contact' in patient_field_names:
                data['emergency_contact'] = f"+1-555-{np.random.randint(100, 999)}-{np.random.randint(1000, 9999)}"
            if 'medical_history' in patient_field_names:
                data['medical_history'] = 'Synthetic medical history for FDS demonstration.'
            if 'notes' in patient_field_names:
                data['notes'] = 'SYNTHETIC RECORD - MediAnalytics Platform'
            if 'created_by' in patient_field_names and admin_user:
                data['created_by'] = admin_user

            try:
                # If model has unique constraint on patient_id, get_or_create or create
                if 'patient_id' in data:
                    patient, _ = Patient.objects.get_or_create(patient_id=data['patient_id'], defaults=data)
                else:
                    patient = Patient.objects.create(**data)
                created_patients.append(patient)
            except Exception as e:
                # Fallback on minimum fields
                try:
                    patient = Patient.objects.create(**{k: v for k, v in data.items() if k in ['first_name', 'last_name', 'gender', 'age']})
                    created_patients.append(patient)
                except Exception:
                    pass

            if (i + 1) % 100 == 0 or (i + 1) == count:
                self.stdout.write(f"  -> Generated {len(created_patients)} / {count} patients")

        self.stdout.write(self.style.SUCCESS(f"Successfully created {len(created_patients)} patient records."))
        return created_patients

    def generate_medical_records(self, patients_list, count, admin_user):
        """Generates synthetic medical checkups and clinical records."""
        try:
            from medical_records.models import MedicalRecord
        except ImportError:
            self.stdout.write(self.style.WARNING('Could not import MedicalRecord model. Skipping record population.'))
            return

        if not patients_list:
            patients_list = list(MedicalRecord._meta.get_field('patient').related_model.objects.all())
            if not patients_list:
                self.stdout.write(self.style.WARNING('No patients found to attach medical records to.'))
                return

        self.stdout.write(f'\nCreating {count} synthetic clinical records...')
        record_fields = {f.name for f in MedicalRecord._meta.get_fields()}

        diagnoses = [
            'Coronary Artery Disease', 'Acute Myocardial Infarction', 'Hypertension Stage 2',
            'Arrhythmia', 'Type 2 Diabetes Mellitus', 'Hyperlipidemia',
            'Non-cardiac Chest Pain', 'Aortic Stenosis', 'Normal Clinical Evaluation',
            'Congestive Heart Failure', 'Stable Angina Pectoris'
        ]

        symptoms_list = [
            'Substernal chest tightness, radiating to left arm',
            'Shortness of breath on mild exertion, diaphoresis',
            'Palpitations and occasional lightheadedness',
            'Atypical epigastric discomfort, nausea',
            'Asymptomatic routine annual screening',
            'Fatigue, generalized weakness, elevated resting pulse'
        ]

        doctors = [
            'Dr. Sarah Lin, MD (Cardiology)', 'Dr. Marcus Vance, MD (Internal Medicine)',
            'Dr. Elena Rostova, MD (Emergency Medicine)', 'Dr. David Okafor, MD (Cardiology)'
        ]

        created_records = []
        for i in range(count):
            patient = np.random.choice(patients_list)
            outcome = np.random.choice(['Positive', 'Negative', 'Inconclusive'], p=[0.35, 0.50, 0.15])

            # Biomarkers and clinical metrics dependent on outcome
            if outcome == 'Positive':
                hr = int(np.random.normal(loc=98, scale=18))
                sbp = int(np.random.normal(loc=152, scale=16))
                dbp = int(np.random.normal(loc=96, scale=10))
                chol = float(np.random.normal(loc=248, scale=35))
                gluc = float(np.random.normal(loc=165, scale=40))
                ck_mb = round(float(np.random.uniform(16.0, 75.0)), 2)
                troponin = round(float(np.random.exponential(scale=0.8) + 0.15), 3)
                diagnosis = np.random.choice(['Acute Myocardial Infarction', 'Coronary Artery Disease', 'Hypertension Stage 2'])
            elif outcome == 'Negative':
                hr = int(np.random.normal(loc=74, scale=9))
                sbp = int(np.random.normal(loc=122, scale=10))
                dbp = int(np.random.normal(loc=78, scale=8))
                chol = float(np.random.normal(loc=185, scale=25))
                gluc = float(np.random.normal(loc=92, scale=14))
                ck_mb = round(float(np.random.uniform(0.5, 4.8)), 2)
                troponin = round(float(np.random.uniform(0.001, 0.038)), 3)
                diagnosis = np.random.choice(['Normal Clinical Evaluation', 'Non-cardiac Chest Pain', 'Hyperlipidemia'])
            else:  # Inconclusive
                hr = int(np.random.normal(loc=84, scale=12))
                sbp = int(np.random.normal(loc=138, scale=14))
                dbp = int(np.random.normal(loc=86, scale=9))
                chol = float(np.random.normal(loc=215, scale=30))
                gluc = float(np.random.normal(loc=125, scale=25))
                ck_mb = round(float(np.random.uniform(4.5, 8.5)), 2)
                troponin = round(float(np.random.uniform(0.035, 0.075)), 3)
                diagnosis = np.random.choice(['Arrhythmia', 'Stable Angina Pectoris', 'Type 2 Diabetes Mellitus'])

            # Add occasional controlled outliers
            if np.random.rand() < 0.03:
                hr = int(np.random.choice([38, 208, 225]))
            if np.random.rand() < 0.02:
                sbp = int(np.random.choice([218, 235]))

            days_ago = np.random.randint(1, 365)
            visit_date = date.today() - timedelta(days=days_ago)

            data = {}
            if 'patient' in record_fields:
                data['patient'] = patient
            if 'doctor' in record_fields:
                data['doctor'] = np.random.choice(doctors)
            if 'doctor_name' in record_fields:
                data['doctor_name'] = np.random.choice(doctors)
            if 'record_id' in record_fields:
                data['record_id'] = f"REC-{i+1:05d}"
            if 'test_date' in record_fields:
                data['test_date'] = visit_date
            if 'visit_date' in record_fields:
                data['visit_date'] = visit_date
            if 'record_date' in record_fields:
                data['record_date'] = visit_date
            if 'diagnosis' in record_fields:
                data['diagnosis'] = diagnosis
            if 'symptoms' in record_fields:
                data['symptoms'] = np.random.choice(symptoms_list)
            if 'heart_rate' in record_fields:
                data['heart_rate'] = hr
            if 'bp_systolic' in record_fields:
                data['bp_systolic'] = sbp
            if 'systolic_bp' in record_fields:
                data['systolic_bp'] = sbp
            if 'bp_diastolic' in record_fields:
                data['bp_diastolic'] = dbp
            if 'diastolic_bp' in record_fields:
                data['diastolic_bp'] = dbp
            if 'blood_pressure' in record_fields:
                data['blood_pressure'] = f"{sbp}/{dbp}"
            if 'cholesterol' in record_fields:
                data['cholesterol'] = round(chol, 1)
            if 'blood_glucose' in record_fields:
                data['blood_glucose'] = round(gluc, 1)
            if 'ck_mb' in record_fields:
                data['ck_mb'] = ck_mb
            if 'troponin' in record_fields:
                data['troponin'] = troponin
            if 'outcome' in record_fields:
                data['outcome'] = outcome
            if 'notes' in record_fields:
                data['notes'] = f"SYNTHETIC VISIT NOTE: {diagnosis}. Monitored for clinical teaching."
            if 'treatment' in record_fields:
                data['treatment'] = 'Standard protocol administered based on observed vitals.'
            if 'created_by' in record_fields and admin_user:
                data['created_by'] = admin_user

            try:
                rec = MedicalRecord.objects.create(**data)
                created_records.append(rec)
            except Exception as ex:
                if i == 0:
                    self.stdout.write(self.style.ERROR(f"MedicalRecord creation error: {ex}"))
                pass

            if (i + 1) % 250 == 0 or (i + 1) == count:
                self.stdout.write(f"  -> Generated {len(created_records)} / {count} clinical records")

        self.stdout.write(self.style.SUCCESS(f"Successfully created {len(created_records)} clinical records."))

    def generate_csv_dataset(self, num_rows):
        """
        Creates synthetic CSV dataset with controlled real-world anomalies:
        - 5% missing values (NaN)
        - 3% duplicate rows
        - Inconsistent categorical labels ('male', 'Male', 'MALE', 'M')
        - Numerical outliers (HR > 200, extreme BP/Cholesterol)
        - Outcomes: Positive, Negative, Inconclusive
        """
        self.stdout.write(f'\nGenerating synthetic CSV dataset ({num_rows} rows) with controlled anomalies...')

        # Ensure directory exists
        base_dir = getattr(settings, 'BASE_DIR', None)
        if base_dir:
            csv_dir = os.path.join(str(base_dir), 'media', 'uploaded_datasets')
        else:
            csv_dir = os.path.join('media', 'uploaded_datasets')
        os.makedirs(csv_dir, exist_ok=True)
        csv_path = os.path.join(csv_dir, 'sample_healthcare_data.csv')

        # Baseline generation
        patient_ids = [f"SYN-PAT-{i+1:04d}" for i in range(num_rows)]
        ages = np.clip(np.random.normal(loc=55, scale=15, size=num_rows).astype(int), 18, 90)

        # Inconsistent gender labels: 'male', 'Male', 'MALE', 'M', 'female', 'Female', 'FEMALE', 'F'
        male_variants = ['Male', 'male', 'MALE', 'M']
        female_variants = ['Female', 'female', 'FEMALE', 'F']
        genders = []
        for _ in range(num_rows):
            if np.random.rand() > 0.5:
                genders.append(np.random.choice(male_variants, p=[0.70, 0.15, 0.08, 0.07]))
            else:
                genders.append(np.random.choice(female_variants, p=[0.70, 0.15, 0.08, 0.07]))

        outcomes = np.random.choice(['Positive', 'Negative', 'Inconclusive'], size=num_rows, p=[0.35, 0.50, 0.15])

        heart_rates = []
        systolic_bps = []
        diastolic_bps = []
        cholesterols = []
        blood_glucoses = []
        ck_mbs = []
        troponins = []

        for outcome in outcomes:
            if outcome == 'Positive':
                hr = float(np.random.normal(loc=98, scale=16))
                sbp = float(np.random.normal(loc=154, scale=18))
                dbp = float(np.random.normal(loc=95, scale=12))
                chol = float(np.random.normal(loc=250, scale=38))
                gluc = float(np.random.normal(loc=168, scale=42))
                ck = round(float(np.random.uniform(15.0, 78.0)), 2)
                trop = round(float(np.random.exponential(scale=0.9) + 0.12), 3)
            elif outcome == 'Negative':
                hr = float(np.random.normal(loc=74, scale=9))
                sbp = float(np.random.normal(loc=122, scale=11))
                dbp = float(np.random.normal(loc=78, scale=8))
                chol = float(np.random.normal(loc=186, scale=26))
                gluc = float(np.random.normal(loc=94, scale=15))
                ck = round(float(np.random.uniform(0.5, 4.9)), 2)
                trop = round(float(np.random.uniform(0.001, 0.038)), 3)
            else:  # Inconclusive
                hr = float(np.random.normal(loc=85, scale=12))
                sbp = float(np.random.normal(loc=136, scale=14))
                dbp = float(np.random.normal(loc=86, scale=10))
                chol = float(np.random.normal(loc=218, scale=32))
                gluc = float(np.random.normal(loc=128, scale=28))
                ck = round(float(np.random.uniform(4.5, 8.8)), 2)
                trop = round(float(np.random.uniform(0.034, 0.082)), 3)

            heart_rates.append(round(hr, 1))
            systolic_bps.append(round(sbp, 1))
            diastolic_bps.append(round(dbp, 1))
            cholesterols.append(round(chol, 1))
            blood_glucoses.append(round(gluc, 1))
            ck_mbs.append(ck)
            troponins.append(trop)

        # Inject numerical outliers (heart rate > 200, BP > 220, Chol > 380, Gluc > 350)
        outlier_indices = np.random.choice(num_rows, size=int(num_rows * 0.04), replace=False)
        for idx in outlier_indices:
            anomaly_type = np.random.choice(['hr', 'bp', 'chol', 'gluc'])
            if anomaly_type == 'hr':
                heart_rates[idx] = float(np.random.choice([208.0, 215.0, 228.0]))
            elif anomaly_type == 'bp':
                systolic_bps[idx] = float(np.random.choice([225.0, 240.0]))
                diastolic_bps[idx] = float(np.random.choice([128.0, 138.0]))
            elif anomaly_type == 'chol':
                cholesterols[idx] = float(np.random.choice([390.0, 425.0]))
            elif anomaly_type == 'gluc':
                blood_glucoses[idx] = float(np.random.choice([360.0, 410.0]))

        # Assemble DataFrame
        df = pd.DataFrame({
            'Patient_ID': patient_ids,
            'Age': ages,
            'Gender': genders,
            'Heart_Rate': heart_rates,
            'Systolic_BP': systolic_bps,
            'Diastolic_BP': diastolic_bps,
            'Cholesterol': cholesterols,
            'Blood_Glucose': blood_glucoses,
            'CK_MB': ck_mbs,
            'Troponin': troponins,
            'Outcome': outcomes
        })

        # Inject ~5% missing values (np.nan) in various numerical & categorical columns
        cols_for_nans = ['Heart_Rate', 'Systolic_BP', 'Diastolic_BP', 'Cholesterol', 'Blood_Glucose', 'CK_MB', 'Troponin', 'Gender']
        for col in cols_for_nans:
            nan_mask = np.random.rand(num_rows) < 0.05
            df.loc[nan_mask, col] = np.nan

        # Inject ~3% duplicate records
        num_duplicates = max(1, int(num_rows * 0.03))
        duplicate_source_indices = np.random.choice(num_rows, size=num_duplicates, replace=False)
        duplicate_rows = df.iloc[duplicate_source_indices].copy()
        df = pd.concat([df, duplicate_rows], ignore_index=True)

        # Save to CSV
        df.to_csv(csv_path, index=False)
        self.stdout.write(self.style.SUCCESS(f"Saved CSV dataset to: {csv_path} ({len(df)} rows)"))
        return csv_path

    def register_uploaded_dataset(self, csv_path, admin_user, raw_row_count):
        """Registers the generated CSV file inside datasets.UploadedDataset model."""
        try:
            from datasets.models import UploadedDataset
        except ImportError:
            self.stdout.write(self.style.WARNING('Could not import UploadedDataset model. Skipping database registration.'))
            return

        dataset_fields = {f.name for f in UploadedDataset._meta.get_fields()}
        rel_file_path = os.path.join('uploaded_datasets', os.path.basename(csv_path)).replace('\\', '/')

        data = {}
        if 'name' in dataset_fields:
            data['name'] = 'Synthetic Healthcare Dataset (Demonstration)'
        if 'title' in dataset_fields:
            data['title'] = 'Synthetic Healthcare Dataset (Demonstration)'
        if 'file' in dataset_fields:
            data['file'] = rel_file_path
        if 'csv_file' in dataset_fields:
            data['csv_file'] = rel_file_path
        if 'dataset_file' in dataset_fields:
            data['dataset_file'] = rel_file_path
        if 'data_file' in dataset_fields:
            data['data_file'] = rel_file_path
        if 'uploaded_by' in dataset_fields and admin_user:
            data['uploaded_by'] = admin_user
        if 'user' in dataset_fields and admin_user:
            data['user'] = admin_user
        if 'description' in dataset_fields:
            data['description'] = (
                'Controlled synthetic clinical benchmark dataset containing 500+ records with real-world anomalies '
                '(5% missing values, 3% duplicate entries, inconsistent gender categoricals, and cardiovascular outliers) '
                'for demonstration of FDS data engineering & analytics pipelines.'
            )
        if 'row_count' in dataset_fields:
            data['row_count'] = raw_row_count
        if 'total_rows' in dataset_fields:
            data['total_rows'] = raw_row_count
        if 'column_count' in dataset_fields:
            data['column_count'] = 11
        if 'total_columns' in dataset_fields:
            data['total_columns'] = 11
        if 'is_cleaned' in dataset_fields:
            data['is_cleaned'] = False

        try:
            # Check if matching record exists
            if 'name' in data:
                ds, created = UploadedDataset.objects.get_or_create(name=data['name'], defaults=data)
            elif 'title' in data:
                ds, created = UploadedDataset.objects.get_or_create(title=data['title'], defaults=data)
            else:
                ds = UploadedDataset.objects.create(**data)
                created = True

            action_str = 'Created' if created else 'Found existing'
            self.stdout.write(self.style.SUCCESS(f"{action_str} UploadedDataset record in database."))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Note on registering UploadedDataset: {str(e)}'))
