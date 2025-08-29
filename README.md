# SASTRA Hall Plan Generation
[![CodeQL Advanced](https://github.com/SASTRA-Projects/SASTRA-Timetable/actions/workflows/codeql.yml/badge.svg)](https://github.com/SASTRA-Projects/HallPlan/actions/workflows/codeql.yml)

## **📘 Project Overview**

The **SASTRA Hall Plan Generation System** automates the creation of exam hall plans and seating arrangements at [SASTRA DEEMED TO BE UNIVERSITY](https://www.sastra.edu), building on top of [SASTRA Timetable Generation](https://github.com/SASTRA-Projects/Timetable) project to reduce manual effort, minimize errors, and ensure fairness.
This system replaces the manual process of hall allocation and seating chart creation with an intelligent, automated solution.

## **🚀 Features**

* **Automated Seating Arrangement:** Dynamically generates optimized seating plans based on student enrollment and hall capacity.
* **Conflict-Free Allocation:** Implements rules to prevent students from the same class or department from being seated adjacently.
* **Customizable Rules Engine:** Supports various constraints like spacing requirements, block allocation for different departments, and varying room capacities.
* **Invigilator Assignment:** Module for assigning faculty invigilators to halls, ensuring proper supervision.
* **Exportable Reports:** Generates printable attendance sheets and seating charts for notice boards and invigilators in form of Excel sheets.
* **User-Friendly Interface:** Built with a responsive front end for easy data entry and plan generation.

## **🛠️ Tools & Technologies Used**

* **Backend:** [Flask](https://flask.palletsprojects.com/en/stable/) (Python)
* **Frontend:** [HTML](https://html.com/), [CSS](https://css3.com/), [JavaScript](https://www.javascript.com/)
* **Database:** [MySQL](https://www.mysql.com/)
* **Visualization:** [Mermaid.js](https://mermaid-js.github.io/) for ER diagram

## **🎯 Project Vision & Mission**

At SASTRA DEEMED UNIVERSITY, our focus on academic integrity is paramount.
This project supports that mission by removing the administrative burden of manual hall plan creation, allowing staff to focus on conducting examinations smoothly.

Our goal is simple: **Let administrators focus on conducting fair exams — not on drawing seating charts.**

The system is designed to prevent common issues that arise during manual planning, such as:

* Accidental seating of friends or classmates together.
* Inefficient use of examination hall space.
* Last-minute confusion regarding student allocation.
* Errors in attendance sheets.

## **⚔️ Challenges in the Current Manual System**

Creating an examination hall plan manually is a high-stakes, pressure-filled task. It requires immense attention to detail and coordination, and even small mistakes can lead to significant problems on the day of the exam.

### **Problems Faced**

* **High Risk of Errors:** Manually assigning seats for thousands of students is prone to errors, where one mistake can cause widespread confusion and delays.
* **Time-Consuming and Repetitive:** The process must be repeated for each exam session, taking up valuable time and diverting staff from other tasks.
* **Inefficient Space Utilization:** Without an algorithmic approach, halls may be under or overcrowded, leading to wasted space or the need for additional rooms.
* **Integrity Concerns:** Manual seating plans struggle to enforce rules, like maintaining proper distance between students or separating those from the same course, raising the risk of academic dishonesty.

This project addresses these issues by introducing automation, consistency, and reliability to the examination process.

## **🏗️ System & Repository Structure**

```
HallPlan/                   ← Main project (exam-specific logic)
├── Timetable/              ← Submodule (core scheduling engine)
│   ├── app.py              ← Flask entry point (for Timetable/)
│   ├── database.py         ← Database logic (models, schemas)
│   ├── fetch_date.py       ← API endpoints
│   └── …                   ← Other core files
├── app.py                  ← Flask entry point (for HallPlan/)
├── generate_hallplan.py    ← Extensions and exam-specific logic
└── README.md               ← Overview and setup instructions
```
The [Timetable](https://github.com/SASTRA-Projects/Timetable) repository contains the database logic, which [HallPlan](https://github.com/SASTRA-Projects/HallPlan) extends for its specific purpose.

## **⚡ Getting Started**

### **Prerequisites**

* [Python](https://www.python.org/downloads/) (>= 3.11)
* [MySQL Client](https://dev.mysql.com/downloads/) (Optional)

### **Installation**

1. Clone the Repository (with Submodules):
   Because this project includes the [Timetable](https://github.com/SASTRA-Projects/Timetable) repository inside it, you must use a special clone command to download both at the same time.
```sh
   git clone --recurse-submodules https://github.com/SASTRA-Projects/HallPlan/
   cd HallPlan
```
   **Note:** If you forgot to use --recurse-submodules, you can run `git submodule update --init --recursive` inside the [HallPlan](https://github.com/SASTRA-Projects/HallPlan) directory to fix it.

2. If [Timetable](https://github.com/SASTRA-Projects/Timetable) logic needed to be modified:
   Go inside Timetable sub-folder using,
```sh
   cd Timetable
```
   or, see [Timetable/README.md](/Timetable/README.md)

3. Set Up a Virtual Environment:

- <details>
    <summary><strong>Linux/macOS</strong></summary>

    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```
  </details>

- <details>
    <summary><strong>Windows (CMD)</strong></summary>

    ```sh
      python -m venv venv
      venv\Scripts\activate
    ```
  </details>

- <details>
    <summary><strong>Windows (PowerShell)</strong></summary>

    ```sh
      python -m venv venv
      .\venv\Scripts\Activate.ps1
    ```
  </details>

4. **Install Dependencies:**
```sh
  pip install -r requirements.txt
```


4. **Configure MySQL Database:**
Create a `.env` file for your DB credentials.

5. **Run the Application:**

- <details>
    <summary><strong>In Developer Mode</strong></summary>

    ```sh
      python app.py
    ```
  </details>

- <details>
    <summary><strong>In production level</strong></summary>

    - **Windows:**
    ```sh
      waitress-serve --host=localhost --port=5000 app:app
    ```

    - **Linux/macOS:**
    ```sh
      gunicorn app:app --bind 0.0.0.0:5000
    ```
</details>

6. **Access the Web Interface:**
Open [http://localhost:5000](http://localhost:5000) in your browser.

## 📊 System Overview (Coming Soon)
*A high-level system diagram showing module interaction will be added shortly.*

## **🧠 Future Scope**

* **Visual Hall Designer:** An interface to visually design the layout of benches and seats in each examination hall.
* **Advanced Analytics:** Provide reports on hall utilization, invigilator duty hours, and exam session statistics.

## **📜 License**

This project is licensed under the **Apache License 2.0**. See the [LICENSE](LICENSE) file for detailed information.

Additional attribution details can be found in the [NOTICE](NOTICE) file.

## **🤝 Contributing**

Contributions are welcome! We'd love your help to improve this system.

Please follow our [Code of Conduct](CODE_OF_CONDUCT.md) to maintain a collaborative and respectful environment.

1. **Fork the Repository:** Click the ["Fork"](https://github.com/SASTRA-Projects/HallPlan/fork) button on the [SASTRA-Projects/HallPlan GitHub page](https://github.com/SASTRA-Projects/HallPlan).
2. **Create a Branch:**
```sh
  git checkout -b branch-name
```
3. **Commit Your Changes:**
```sh
  git commit -m "Add your feature description"
```
4. **Push to Your Branch:**
```sh
  git push origin feature-name
```
5. **Submit a Pull Request:** Navigate to the **Pull Requests** tab on GitHub and submit your PR.

---

Happy Coding 🚀! Let’s build something awesome together!

If you have any questions or run into issues, please feel free to open an issue on GitHub!
