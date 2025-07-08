-- Create database
CREATE DATABASE company_db;
\c company_db;

-- Create tables
CREATE TABLE department (
    dept_id INTEGER PRIMARY KEY,
    dept_name VARCHAR(100),
    location VARCHAR(100),
    budget NUMERIC,
    manager_id INTEGER
);

CREATE TABLE employee (
    emp_id INTEGER PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    hire_date DATE,
    dept_id INTEGER REFERENCES department(dept_id),
    job_title VARCHAR(100),
    manager_id INTEGER REFERENCES employee(emp_id)
);

-- Add foreign key constraint to department for manager_id
ALTER TABLE department 
ADD CONSTRAINT fk_department_manager 
FOREIGN KEY (manager_id) REFERENCES employee(emp_id);

CREATE TABLE salary (
    salary_id INTEGER PRIMARY KEY,
    emp_id INTEGER REFERENCES employee(emp_id),
    base_salary NUMERIC,
    bonus NUMERIC,
    effective_date DATE
);

-- New project table
CREATE TABLE project (
    project_id INTEGER PRIMARY KEY,
    project_name VARCHAR(100),
    start_date DATE,
    end_date DATE,
    budget NUMERIC,
    status VARCHAR(20) CHECK (status IN ('Planning', 'In Progress', 'Completed', 'On Hold', 'Cancelled')),
    dept_id INTEGER REFERENCES department(dept_id)
);

-- Project assignment table to connect employees and projects
CREATE TABLE project_assignment (
    assignment_id INTEGER PRIMARY KEY,
    project_id INTEGER REFERENCES project(project_id),
    emp_id INTEGER REFERENCES employee(emp_id),
    role VARCHAR(50),
    assignment_date DATE,
    completion_date DATE
);

-- New performance review table
CREATE TABLE performance_review (
    review_id INTEGER PRIMARY KEY,
    emp_id INTEGER REFERENCES employee(emp_id),
    review_date DATE,
    reviewer_id INTEGER REFERENCES employee(emp_id),
    performance_score NUMERIC CHECK (performance_score BETWEEN 1 AND 5),
    comments TEXT
);

-- Insert sample data
INSERT INTO department (dept_id, dept_name, location, budget, manager_id) VALUES
(1, 'Engineering', 'Building A', 1000000, NULL),
(2, 'Marketing', 'Building B', 500000, NULL),
(3, 'Human Resources', 'Building A', 300000, NULL),
(4, 'Finance', 'Building C', 700000, NULL),
(5, 'Sales', 'Building B', 800000, NULL),
(6, 'Research & Development', 'Building D', 1200000, NULL),
(7, 'Customer Support', 'Building C', 400000, NULL),
(8, 'Information Technology', 'Building A', 900000, NULL);

INSERT INTO employee (emp_id, first_name, last_name, email, phone, hire_date, dept_id, job_title, manager_id) VALUES
(101, 'John', 'Smith', 'john.smith@company.com', '555-1001', '2020-01-15', 1, 'Senior Developer', NULL),
(102, 'Jane', 'Doe', 'jane.doe@company.com', '555-1002', '2019-05-20', 1, 'Developer', 101),
(103, 'Michael', 'Johnson', 'michael.johnson@company.com', '555-1003', '2021-03-10', 2, 'Marketing Manager', NULL),
(104, 'Emily', 'Williams', 'emily.williams@company.com', '555-1004', '2018-11-08', 2, 'Marketing Specialist', 103),
(105, 'David', 'Brown', 'david.brown@company.com', '555-1005', '2022-02-15', 3, 'HR Director', NULL),
(106, 'Sarah', 'Jones', 'sarah.jones@company.com', '555-1006', '2020-07-22', 3, 'HR Specialist', 105),
(107, 'Robert', 'Miller', 'robert.miller@company.com', '555-1007', '2019-09-30', 4, 'Finance Director', NULL),
(108, 'Jennifer', 'Davis', 'jennifer.davis@company.com', '555-1008', '2021-06-12', 4, 'Accountant', 107),
(109, 'Thomas', 'Wilson', 'thomas.wilson@company.com', '555-1009', '2020-03-25', 5, 'Sales Director', NULL),
(110, 'Lisa', 'Moore', 'lisa.moore@company.com', '555-1010', '2021-05-18', 5, 'Sales Representative', 109),
(111, 'Daniel', 'Taylor', 'daniel.taylor@company.com', '555-1011', '2019-10-15', 6, 'Research Director', NULL),
(112, 'Jessica', 'Anderson', 'jessica.anderson@company.com', '555-1012', '2022-01-10', 6, 'Research Scientist', 111),
(113, 'Matthew', 'Thomas', 'matthew.thomas@company.com', '555-1013', '2020-11-05', 7, 'Support Manager', NULL),
(114, 'Amanda', 'Jackson', 'amanda.jackson@company.com', '555-1014', '2021-08-20', 7, 'Support Specialist', 113),
(115, 'Christopher', 'White', 'christopher.white@company.com', '555-1015', '2018-12-03', 8, 'IT Director', NULL),
(116, 'Elizabeth', 'Harris', 'elizabeth.harris@company.com', '555-1016', '2019-06-15', 8, 'System Administrator', 115),
(117, 'Andrew', 'Martin', 'andrew.martin@company.com', '555-1017', '2020-08-10', 1, 'QA Engineer', 101),
(118, 'Olivia', 'Thompson', 'olivia.thompson@company.com', '555-1018', '2021-04-22', 2, 'Content Creator', 103),
(119, 'James', 'Garcia', 'james.garcia@company.com', '555-1019', '2022-03-15', 3, 'Recruiter', 105),
(120, 'Sophia', 'Martinez', 'sophia.martinez@company.com', '555-1020', '2019-11-12', 4, 'Financial Analyst', 107),
(121, 'Ryan', 'Clark', 'ryan.clark@company.com', '555-1021', '2022-04-15', 1, 'Frontend Developer', 101),
(122, 'Emma', 'Lewis', 'emma.lewis@company.com', '555-1022', '2021-09-05', 1, 'Backend Developer', 101),
(123, 'Nathan', 'Walker', 'nathan.walker@company.com', '555-1023', '2020-10-22', 2, 'Digital Marketing Specialist', 103),
(124, 'Victoria', 'Hall', 'victoria.hall@company.com', '555-1024', '2021-07-18', 2, 'SEO Specialist', 103),
(125, 'William', 'Young', 'william.young@company.com', '555-1025', '2022-01-20', 3, 'Benefits Coordinator', 105),
(126, 'Grace', 'Allen', 'grace.allen@company.com', '555-1026', '2019-08-11', 4, 'Budget Analyst', 107),
(127, 'Benjamin', 'Scott', 'benjamin.scott@company.com', '555-1027', '2021-02-14', 5, 'Sales Representative', 109),
(128, 'Mia', 'Green', 'mia.green@company.com', '555-1028', '2022-05-10', 5, 'Business Development', 109),
(129, 'Alexander', 'Baker', 'alexander.baker@company.com', '555-1029', '2021-11-16', 6, 'Research Analyst', 111),
(130, 'Chloe', 'Adams', 'chloe.adams@company.com', '555-1030', '2020-06-25', 7, 'Support Specialist', 113),
(131, 'Lucas', 'Nelson', 'lucas.nelson@company.com', '555-1031', '2021-10-05', 8, 'Network Administrator', 115),
(132, 'Zoe', 'Hill', 'zoe.hill@company.com', '555-1032', '2022-03-28', 8, 'Security Specialist', 115),
(133, 'Dylan', 'Rivera', 'dylan.rivera@company.com', '555-1033', '2020-07-09', 1, 'Mobile Developer', 101),
(134, 'Abigail', 'Mitchell', 'abigail.mitchell@company.com', '555-1034', '2021-08-17', 6, 'Data Scientist', 111),
(135, 'Ethan', 'Roberts', 'ethan.roberts@company.com', '555-1035', '2022-02-11', 7, 'Customer Success Manager', 113),
(136, 'Isabella', 'Carter', 'isabella.carter@company.com', '555-1036', '2019-11-30', 4, 'Compliance Officer', 107),
(137, 'Mason', 'Phillips', 'mason.phillips@company.com', '555-1037', '2021-01-15', 8, 'Database Administrator', 115),
(138, 'Lily', 'Evans', 'lily.evans@company.com', '555-1038', '2022-04-05', 2, 'Social Media Manager', 103),
(139, 'Jacob', 'Torres', 'jacob.torres@company.com', '555-1039', '2020-09-15', 5, 'Key Account Manager', 109),
(140, 'Hannah', 'Nguyen', 'hannah.nguyen@company.com', '555-1040', '2021-06-22', 3, 'Training Coordinator', 105);

-- Update department managers now that employees exist
UPDATE department SET manager_id = 101 WHERE dept_id = 1;
UPDATE department SET manager_id = 103 WHERE dept_id = 2;
UPDATE department SET manager_id = 105 WHERE dept_id = 3;
UPDATE department SET manager_id = 107 WHERE dept_id = 4;
UPDATE department SET manager_id = 109 WHERE dept_id = 5;
UPDATE department SET manager_id = 111 WHERE dept_id = 6;
UPDATE department SET manager_id = 113 WHERE dept_id = 7;
UPDATE department SET manager_id = 115 WHERE dept_id = 8;

INSERT INTO salary (salary_id, emp_id, base_salary, bonus, effective_date) VALUES
(1001, 101, 95000, 8000, '2023-01-01'),
(1002, 102, 75000, 4000, '2023-01-01'),
(1003, 103, 85000, 7000, '2023-01-01'),
(1004, 104, 65000, 3000, '2023-01-01'),
(1005, 105, 90000, 8000, '2023-01-01'),
(1006, 106, 60000, 2000, '2023-01-01'),
(1007, 107, 100000, 10000, '2023-01-01'),
(1008, 108, 70000, 3500, '2023-01-01'),
(1009, 109, 95000, 9000, '2023-01-01'),
(1010, 110, 65000, 5000, '2023-01-01'),
(1011, 111, 105000, 12000, '2023-01-01'),
(1012, 112, 80000, 5000, '2023-01-01'),
(1013, 113, 85000, 6000, '2023-01-01'),
(1014, 114, 55000, 2500, '2023-01-01'),
(1015, 115, 100000, 9000, '2023-01-01'),
(1016, 116, 75000, 4000, '2023-01-01'),
(1017, 117, 70000, 3500, '2023-01-01'),
(1018, 118, 60000, 2500, '2023-01-01'),
(1019, 119, 65000, 3000, '2023-01-01'),
(1020, 120, 80000, 5500, '2023-01-01'),
(1021, 121, 78000, 3500, '2023-01-01'),
(1022, 122, 82000, 4500, '2023-01-01'),
(1023, 123, 67000, 3200, '2023-01-01'),
(1024, 124, 65000, 2800, '2023-01-01'),
(1025, 125, 63000, 2200, '2023-01-01'),
(1026, 126, 75000, 4000, '2023-01-01'),
(1027, 127, 68000, 6500, '2023-01-01'),
(1028, 128, 72000, 7000, '2023-01-01'),
(1029, 129, 85000, 4500, '2023-01-01'),
(1030, 130, 58000, 2000, '2023-01-01'),
(1031, 131, 78000, 3800, '2023-01-01'),
(1032, 132, 82000, 4200, '2023-01-01'),
(1033, 133, 80000, 4000, '2023-01-01'),
(1034, 134, 88000, 5500, '2023-01-01'),
(1035, 135, 72000, 4000, '2023-01-01'),
(1036, 136, 78000, 4500, '2023-01-01'),
(1037, 137, 86000, 4800, '2023-01-01'),
(1038, 138, 63000, 3200, '2023-01-01'),
(1039, 139, 76000, 8000, '2023-01-01'),
(1040, 140, 62000, 2500, '2023-01-01');

-- Insert projects
INSERT INTO project (project_id, project_name, start_date, end_date, budget, status, dept_id) VALUES
(201, 'Website Redesign', '2023-01-10', '2023-06-15', 120000, 'Completed', 1),
(202, 'Mobile App Development', '2023-03-01', '2023-09-30', 200000, 'In Progress', 1),
(203, 'Q2 Marketing Campaign', '2023-04-01', '2023-06-30', 75000, 'Completed', 2),
(204, 'Employee Benefits Review', '2023-02-15', '2023-05-15', 30000, 'Completed', 3),
(205, 'Annual Financial Audit', '2023-01-01', '2023-03-31', 50000, 'Completed', 4),
(206, 'Sales Territory Expansion', '2023-05-01', '2023-12-31', 150000, 'In Progress', 5),
(207, 'New Product Research', '2023-06-01', '2024-01-31', 250000, 'In Progress', 6),
(208, 'Customer Support Portal', '2023-04-15', '2023-11-30', 180000, 'In Progress', 7),
(209, 'Network Infrastructure Upgrade', '2023-07-01', '2023-10-15', 300000, 'Planning', 8),
(210, 'AI Development Initiative', '2023-09-01', '2024-06-30', 500000, 'Planning', 1);

-- Insert project assignments
INSERT INTO project_assignment (assignment_id, project_id, emp_id, role, assignment_date, completion_date) VALUES
(301, 201, 101, 'Project Lead', '2023-01-10', '2023-06-15'),
(302, 201, 102, 'Developer', '2023-01-10', '2023-06-15'),
(303, 201, 117, 'QA Tester', '2023-01-10', '2023-06-15'),
(304, 202, 101, 'Project Lead', '2023-03-01', NULL),
(305, 202, 102, 'Developer', '2023-03-01', NULL),
(306, 202, 117, 'QA Tester', '2023-03-01', NULL),
(307, 203, 103, 'Project Lead', '2023-04-01', '2023-06-30'),
(308, 203, 104, 'Marketing Specialist', '2023-04-01', '2023-06-30'),
(309, 203, 118, 'Content Creator', '2023-04-01', '2023-06-30'),
(310, 204, 105, 'Project Lead', '2023-02-15', '2023-05-15'),
(311, 204, 106, 'HR Specialist', '2023-02-15', '2023-05-15'),
(312, 204, 119, 'Recruiter', '2023-02-15', '2023-05-15'),
(313, 205, 107, 'Project Lead', '2023-01-01', '2023-03-31'),
(314, 205, 108, 'Accountant', '2023-01-01', '2023-03-31'),
(315, 205, 120, 'Financial Analyst', '2023-01-01', '2023-03-31'),
(316, 206, 109, 'Project Lead', '2023-05-01', NULL),
(317, 206, 110, 'Sales Representative', '2023-05-01', NULL),
(318, 207, 111, 'Project Lead', '2023-06-01', NULL),
(319, 207, 112, 'Research Scientist', '2023-06-01', NULL),
(320, 208, 113, 'Project Lead', '2023-04-15', NULL),
(321, 208, 114, 'Support Specialist', '2023-04-15', NULL),
(322, 209, 115, 'Project Lead', '2023-07-01', NULL),
(323, 209, 116, 'System Administrator', '2023-07-01', NULL),
(324, 210, 101, 'Project Lead', '2023-09-01', NULL),
(325, 210, 102, 'Developer', '2023-09-01', NULL),
(326, 210, 111, 'Research Consultant', '2023-09-01', NULL),
(327, 210, 112, 'Research Scientist', '2023-09-01', NULL),
(328, 202, 121, 'Frontend Developer', '2023-03-15', NULL),
(329, 202, 122, 'Backend Developer', '2023-03-15', NULL),
(330, 202, 133, 'Mobile Developer', '2023-04-01', NULL),
(331, 203, 123, 'Digital Marketing Specialist', '2023-04-01', '2023-06-30'),
(332, 203, 124, 'SEO Specialist', '2023-04-10', '2023-06-30'),
(333, 203, 138, 'Social Media Manager', '2023-04-15', '2023-06-30'),
(334, 204, 125, 'Benefits Coordinator', '2023-02-20', '2023-05-15'),
(335, 204, 140, 'Training Coordinator', '2023-03-01', '2023-05-15'),
(336, 205, 126, 'Budget Analyst', '2023-01-15', '2023-03-31'),
(337, 205, 136, 'Compliance Officer', '2023-02-01', '2023-03-31'),
(338, 206, 127, 'Sales Representative', '2023-05-01', NULL),
(339, 206, 128, 'Business Development', '2023-05-15', NULL),
(340, 206, 139, 'Key Account Manager', '2023-06-01', NULL),
(341, 207, 129, 'Research Analyst', '2023-06-10', NULL),
(342, 207, 134, 'Data Scientist', '2023-06-15', NULL),
(343, 208, 130, 'Support Specialist', '2023-04-20', NULL),
(344, 208, 135, 'Customer Success Manager', '2023-05-01', NULL),
(345, 209, 131, 'Network Administrator', '2023-07-01', NULL),
(346, 209, 132, 'Security Specialist', '2023-07-10', NULL),
(347, 209, 137, 'Database Administrator', '2023-07-15', NULL);

-- Insert performance reviews
INSERT INTO performance_review (review_id, emp_id, review_date, reviewer_id, performance_score, comments) VALUES
(401, 102, '2023-05-15', 101, 4.5, 'Excellent work on the website redesign project. Shows great initiative.'),
(402, 104, '2023-06-30', 103, 4.2, 'Very effective in executing marketing campaigns. Good attention to detail.'),
(403, 106, '2023-05-30', 105, 3.8, 'Reliable team member with good HR knowledge. Could improve on process documentation.'),
(404, 108, '2023-04-15', 107, 4.0, 'Good analytical skills and meets deadlines consistently.'),
(405, 110, '2023-07-10', 109, 4.7, 'Outstanding sales performance, exceeded targets by 20%.'),
(406, 112, '2023-08-05', 111, 4.3, 'Innovative researcher with solid technical skills. Published 2 research papers.'),
(407, 114, '2023-06-20', 113, 3.5, 'Good customer service skills, needs to improve on ticket resolution time.'),
(408, 116, '2023-07-25', 115, 4.1, 'Reliable system administrator, handled several critical incidents effectively.'),
(409, 117, '2023-06-15', 101, 3.9, 'Good QA skills with attention to detail. Could be more proactive in suggesting improvements.'),
(410, 118, '2023-07-01', 103, 4.4, 'Excellent content creation, particularly effective in social media campaigns.'),
(411, 119, '2023-06-30', 105, 4.0, 'Good recruitment skills, improved hiring process efficiency.'),
(412, 120, '2023-05-20', 107, 4.2, 'Strong financial analysis skills, particularly in forecasting.'),
(413, 101, '2023-08-15', 115, 4.8, 'Outstanding technical leadership and mentoring of junior developers.'),
(414, 103, '2023-08-10', 109, 4.5, 'Excellent marketing strategy development and team management.'),
(415, 105, '2023-07-20', 107, 4.3, 'Strong leadership in HR initiatives and policy development.'),
(416, 107, '2023-07-15', 111, 4.6, 'Excellent financial management and budget optimization.'),
(417, 121, '2023-06-15', 101, 4.1, 'Skilled frontend developer with good UI/UX sensibilities.'),
(418, 122, '2023-06-20', 101, 4.3, 'Strong backend skills with excellent database knowledge.'),
(419, 123, '2023-07-05', 103, 3.9, 'Good understanding of digital marketing channels and analytics.'),
(420, 124, '2023-07-10', 103, 4.0, 'Strong SEO knowledge with demonstrated results in improving site rankings.'),
(421, 125, '2023-06-15', 105, 3.7, 'Good understanding of benefits programs. Needs to improve communication skills.'),
(422, 126, '2023-05-20', 107, 4.4, 'Excellent financial analysis and reporting skills.'),
(423, 127, '2023-07-15', 109, 4.2, 'Consistently meets sales targets with good customer relationships.'),
(424, 128, '2023-07-20', 109, 4.5, 'Excellent at identifying and developing new business opportunities.'),
(425, 129, '2023-08-10', 111, 4.0, 'Strong analytical skills and attention to detail in research protocols.'),
(426, 130, '2023-06-25', 113, 3.6, 'Good customer service skills. Needs to improve technical knowledge.'),
(427, 131, '2023-08-01', 115, 4.2, 'Strong networking skills with excellent troubleshooting abilities.'),
(428, 132, '2023-08-10', 115, 4.4, 'Excellent security knowledge and proactive in identifying vulnerabilities.'); 