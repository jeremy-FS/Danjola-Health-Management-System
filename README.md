# Hospital Management System

## Overview

This project is a Hospital Management System built using HTML, CSS, Flask, and a database. The system allows for the management of hospital operations such as patient admissions, appointments, and staff management.

## Features

- **Patient Management**: Register new patients, view patient records, and update patient information.
- **Appointment Scheduling**: Schedule, view, and manage patient appointments.
- **Staff Management**: Add, view, and manage hospital staff details.
- **Database Integration**: Uses a database to store and manage all records.
- **Web Interface**: User-friendly web interface for interacting with the system.

## Technologies Used

- **Front-End**: HTML, CSS
- **Back-End**: Flask (Python)
- **Database**: SQLite/MySQL (depending on your setup)
- **Server**: XAMPP

## Installation

### Prerequisites

- [Python](https://www.python.org/downloads/)
- [Flask](https://flask.palletsprojects.com/en/2.0.x/installation/)
- [XAMPP](https://www.apachefriends.org/index.html)

### Setup

1. **Clone the Repository**:

    ```sh
    git clone https://github.com/your-username/hospital-management.git
    cd hospital-management
    ```

2. **Create a Virtual Environment**:

    ```sh
    python -m venv venv
    ```

3. **Activate the Virtual Environment**:

    - On Windows:

        ```sh
        venv\Scripts\activate
        ```

    - On macOS/Linux:

        ```sh
        source venv/bin/activate
        ```

4. **Install the Required Packages**:

    ```sh
    pip install -r requirements.txt
    ```

5. **Set Up the Database**:

    - Make sure XAMPP is running (Apache and MySQL).
    - Create a database named `hospital`.
    - Update the database configuration in your Flask application if necessary (usually found in `main.py` or a similar file).

6. **Run the Application**:

    ```sh
    flask run
    ```

7. **Access the Application**:

    Open your web browser and navigate to `http://127.0.0.1:5000/`.

## Usage

- **Home Page**: Provides an overview of the hospital operations.
- **Patients**: Add new patients, view and manage existing patient records.
- **Appointments**: Schedule new appointments, view and manage existing appointments.
- **Staff**: Add new staff members, view and manage existing staff records.

## Contributing

1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/YourFeature`).
3. Commit your changes (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature/YourFeature`).
5. Open a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

If you have any questions or need further assistance, please contact me at [visheshprajapati1234@gmail.com].

---

