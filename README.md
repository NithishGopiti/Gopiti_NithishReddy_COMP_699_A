## **MemoryWeave — Historical Memory Reconstruction Platform**

### **Overview**

MemoryWeave is a collaborative platform designed to help users build, manage, and validate historical narratives in a structured way. The system allows multiple users to contribute information, review it, and maintain proper version control so that the data remains accurate and reliable over time. The platform focuses on combining user input with validation and conflict management to ensure consistency in historical records.

---

### **Project Objective**

The main goal of this project is to replace unstructured data collection with a controlled and organized system. It allows users to submit historical fragments, review them, and build narratives using a systematic approach. The platform also supports multiple interpretations of the same event using branching and version control.

---

### **Key Features**

* User registration and login with role-based access
* Event creation and management with timeline validation
* Fragment submission with source type and confidence rating
* Review system for approving or rejecting submitted fragments
* Narrative branches to support multiple interpretations
* Revision control with locking mechanism
* Merge request system for combining narrative branches
* Conflict detection and resolution
* Audit logs to track all system activities
* Dashboard with real-time system statistics

---

### **System Requirements**

* Python 3.8 or higher
* Streamlit
* SQLite3
* Pandas
* Plotly

---

### **Installation Steps**

1. Clone or download the project
2. Navigate to the project folder
3. Install required packages using:

```bash
pip install streamlit pandas plotly
```

4. Run the application using:

```bash
streamlit run MemoryReconstructivePlatform.py
```

---

### **Database Configuration**

The system uses SQLite as the database.
Make sure the database path is set correctly in the code:

```python
DB_PATH = "memoryweave.db"
```

The database will be created automatically when the application runs for the first time.

---

### **Default Admin Access**

* Username: admin
* Password: Admin@2026

---

### **System Workflow**

1. User logs into the system
2. Events are created with defined timelines
3. Users submit fragments related to events
4. Editors review and approve or reject fragments
5. Approved fragments are used to build narratives
6. Multiple narrative branches can be created
7. Revisions are added and locked when finalized
8. Merge requests are used to combine branches
9. Conflicts are detected and resolved
10. All actions are recorded in audit logs

---

### **Future Enhancements**

* Notification system for approvals and updates
* Advanced data visualization dashboards
* Role-based fine-grained permissions
* Automatic alerts for conflicts
* Cloud database integration

---

### **Contributors**

Nithish Reddy Gopiti

---

### **Conclusion**

MemoryWeave provides a structured and reliable approach for managing historical data. It ensures collaboration, validation, and consistency while allowing flexibility for different interpretations. The system is designed to be scalable and can be extended further with additional features.

