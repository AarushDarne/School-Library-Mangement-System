# backend/models/book.py
from http.client import SWITCHING_PROTOCOLS
from sqlalchemy import Column, Integer, String, Boolean, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Book(Base):
    __tablename__ = 'books'
    
    id = Column(Integer, primary_key=True)
    isbn = Column(String(13), unique=True)
    title = Column(String(200), nullable=False)
    author = Column(String(200))
    barcode = Column(String(50), unique=True)
    is_donated = Column(Boolean, default=False)
    status = Column(String(20))  # Available, Issued, Lost
    acquisition_date = Column(Date)
# backend/services/barcode_service.py
import barcode
from barcode.writer import ImageWriter
from PIL import Image
from pyzbar.pyzbar import decode

class BarcodeService:
    @staticmethod
    def generate_barcode(isbn):
        EAN = barcode.get_barcode_class('ean13')
        ean = EAN(isbn, writer=ImageWriter())
        filename = f"barcodes/{isbn}"
        ean.save(filename)
        return filename

    @staticmethod
    def scan_barcode(image_path):
        image = Image.open(image_path)
        decoded_objects = decode(image)
        for obj in decoded_objects:
            return obj.data.decode('utf-8')
        return None
# frontend/screens/main_window.py
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                           QPushButton, QLabel, QStackedWidget)
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTpiitle("Library Management System")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create header
        header = QLabel("Library Management System")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("""
            font-size: 24px;
            color: #2c3e50;
            padding: 20px;
        """)
        
        # Create navigation buttons
        self.create_navigation_buttons()
        
        # Add widgets to layout
        layout.addWidget(header)
        layout.addWidget(self.nav_widget)
        layout.addWidget(self.stack)

    def create_navigation_buttons(self):
        self.nav_widget = QWidget()
        nav_layout = QHBoxLayout(self.nav_widget)
        
        buttons = [
            ("Books", self.show_books),
            ("Members", self.show_members),
            ("Issue/Return", self.show_transactions),
            ("Donations", self.show_donations)
        ]
        
        for text, slot in buttons:
            button = QPushButton(text)
            button.setStyleSheet("""
                QPushButton {
                    padding: 10px;
                    background-color: #3498db;
                    color: white;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            button.clicked.connect(slot)
            nav_layout.addWidget(button)
# frontend/screens/book_management.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QTableWidget, QTableWidgetItem)

class BookManagement(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # Create toolbar
        toolbar = QHBoxLayout()
        add_button = QPushButton("Add Book")
        scan_button = QPushButton("Scan Barcode")
        toolbar.addWidget(add_button)
        toolbar.addWidget(scan_button)
        
        # Create table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ISBN", "Title", "Author", "Status", 
            "Donated", "Acquisition Date"
        ])
        
        layout.addLayout(toolbar)
        layout.addWidget(self.table)
        
    def scan_barcode(self):
        # Implement camera/scanner integration
        pass
        
    def add_book(self):
        # Implement add book dialog
        pass
# backend/models/student.py
from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Student(Base):
    __tablename__ = 'students'
    
    id = Column(Integer, primary_key=True)
    roll_number = Column(Integer, nullable=False)
    admission_number = Column(String(20), unique=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50))
    class_name = Column(String(10), nullable=False)  # e.g., "10"
    division = Column(String(2), nullable=False)     # e.g., "A", "B"
    contact_number = Column(String(15))
    parent_contact = Column(String(15))
    email = Column(String(100))
    barcode_id = Column(String(50), unique=True)
    is_active = Column(Boolean, default=True)

    # Relationship with book transactions
    transactions = relationship("BookTransaction", back_populates="student")

class BookTransaction(Base):
    __tablename__ = 'book_transactions'
    
    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books.id'))
    student_id = Column(Integer, ForeignKey('students.id'))
    issue_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    return_date = Column(Date)
    fine_amount = Column(Integer, default=0)
    
    student = relationship("Student", back_populates="transactions")
    book = relationship("Book")
# backend/services/student_service.py
from datetime import datetime
from sqlalchemy.orm import Session
from .models.student import Student

class StudentService:
    def __init__(self, db_session: Session):
        self.session = db_session

    def add_student(self, student_data):
        student = Student(
            roll_number=student_data['roll_number'],
            admission_number=student_data['admission_number'],
            first_name=student_data['first_name'],
            last_name=student_data['last_name'],
            class_name=student_data['class_name'],
            division=student_data['division'],
            contact_number=student_data.get('contact_number'),
            parent_contact=student_data.get('parent_contact'),
            email=student_data.get('email')
        )
        self.session.add(student)
        self.session.commit()
        return student

    def get_students_by_class(self, class_name, division):
        return self.session.query(Student).filter_by(
            class_name=class_name,
            division=division,
            is_active=True
        ).order_by(Student.roll_number).all()

    def get_student_books(self, student_id):
        student = self.session.query(Student).get(student_id)
        return [trans.book for trans in student.transactions 
                if trans.return_date is None]
# frontend/screens/student_management.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QTableWidget, QTableWidgetItem,
                           QComboBox, QLabel, QLineEdit, QFormLayout,
                           QDialog)

class StudentManagementScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Standard library imports
        import os

        # Third-party imports
        from dotenv import load_dotenv

        # Local application imports
        from backend.scheduler import NotificationScheduler
        from backend.services.notification_service import NotificationService

        # Load environment variables at the start
        load_dotenv()

        filter_layout.addWidget(QLabel("Class:"))
        filter_layout.addWidget(self.class_combo)
        filter_layout.addWidget(QLabel("Division:"))
        SMTP_USERNAME=your_email@gmail.com
        SMTP_PASSWORD=your_app_specific_password
        FROM_EMAIL=library@school.com


        # SMTP Configuration
        SMTP_SERVER = "smtp.gmail.com"  # This is a standard value for Gmail
        SMTP_PORT = 587  # Standard TLS port
        SMTP_USERNAME = os.getenv('SMTP_USERNAME')
        SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
        FROM_EMAIL = os.getenv('FROM_EMAIL')

        add_button = QPushButton("Add Student")
        add_button.clicked.connect(self.show_add_student_dialog)
        toolbar.addWidget(add_button)
        
        # Student Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Roll No.", "Admission No.", "Name", 
            "Class", "Division", "Contact", "Books Issued"
        ])
        
        layout.addLayout(filter_layout)
        layout.addLayout(toolbar)
        layout.addWidget(self.table)
        
        # Connect signals
        self.class_combo.currentTextChanged.connect(self.refresh_student_list)
        self.division_combo.currentTextChanged.connect(self.refresh_student_list)

    def refresh_student_list(self):
        # Implementation to refresh the student list based on class/division
        pass

class AddStudentDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Student")
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)
        
        # Create input fields
        self.admission_number = QLineEdit()
        self.roll_number = QLineEdit()
        self.first_name = QLineEdit()
        self.last_name = QLineEdit()
        self.class_combo = QComboBox()
        self.class_combo.addItems([str(i) for i in range(1, 13)])
        self.division_combo = QComboBox()
        self.division_combo.addItems(['A', 'B', 'C', 'D'])
        self.contact = QLineEdit()
        self.parent_contact = QLineEdit()
        self.email = QLineEdit()
        
        # Add fields to form
        layout.addRow("Admission Number:", self.admission_number)
        layout.addRow("Roll Number:", self.roll_number)
        layout.addRow("First Name:", self.first_name)
        layout.addRow("Last Name:", self.last_name)
        layout.addRow("Class:", self.class_combo)
        layout.addRow("Division:", self.division_combo)
        layout.addRow("Contact:", self.contact)
        layout.addRow("Parent Contact:", self.parent_contact)
        layout.addRow("Email:", self.email)
        
        # Add buttons
        button_box = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        
        save_button.clicked.connect(self.save_student)
        cancel_button.clicked.connect(self.reject)
        
        button_box.addWidget(save_button)
        button_box.addWidget(cancel_button)
        layout.addRow(button_box)

    def save_student(self):
        # Implementation to save student data
        pass
# frontend/screens/book_issue.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QTableWidget, QTableWidgetItem,
                           QLabel, QLineEdit)

class BookIssueScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Student Search Section
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter Admission Number or Roll Number")
        search_button = QPushButton("Search")
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        
        # Student Info Section
        self.student_info = QWidget()
        student_layout = QFormLayout(self.student_info)
        self.name_label = QLabel()
        self.class_label = QLabel()
        self.books_issued_label = QLabel()
        
        student_layout.addRow("Name:", self.name_label)
        student_layout.addRow("Class:", self.class_label)
        student_layout.addRow("Books Issued:", self.books_issued_label)
        
        # Book Issue Section
        issue_layout = QHBoxLayout()
        self.book_input = QLineEdit()
        self.book_input.setPlaceholderText("Scan Book Barcode")
        issue_button = QPushButton("Issue Book")
        issue_layout.addWidget(self.book_input)
        issue_layout.addWidget(issue_button)
        
        # Currently Issued Books Table
        self.issued_table = QTableWidget()
        self.issued_table.setColumnCount(4)
        self.issued_table.setHorizontalHeaderLabels([
            "Book Title", "Issue Date", "Due Date", "Return"
        ])
        
        layout.addLayout(search_layout)
        layout.addWidget(self.student_info)
        layout.addLayout(issue_layout)
        layout.addWidget(self.issued_table)
# backend/services/report_service.py
from datetime import datetime
import pandas as pd

class ReportService:
    def __init__(self, db_session):
        self.session = db_session

    def generate_class_report(self, class_name, division):
        # Query for class statistics
        students = self.session.query(Student).filter_by(
            class_name=class_name,
            division=division
        ).all()
        
        data = []
        for student in students:
            active_books = len([t for t in student.transactions 
                              if t.return_date is None])
            total_books = len(student.transactions)
            
            data.append({
                'Roll No': student.roll_number,
                'Name': f"{student.first_name} {student.last_name}",
                'Books Currently Issued': active_books,
                'Total Books Issued': total_books
            })
        
        df = pd.DataFrame(data)
        return df

    def export_to_excel(self, class_name, division):
        df = self.generate_class_report(class_name, division)
        filename = f"Class_{class_name}_{division}_Report_{datetime.now().strftime('%Y%m%d')}.xlsx"
        df.to_excel(filename, index=False)
        return filename
# backend/models/notification.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class TeacherContact(Base):
    __tablename__ = 'teacher_contacts'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    class_name = Column(String(10), nullable=False)
    division = Column(String(2), nullable=False)
    is_active = Column(Boolean, default=True)

class Notification(Base):
    __tablename__ = 'notifications'
    
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    book_id = Column(Integer, ForeignKey('books.id'))
    teacher_id = Column(Integer, ForeignKey('teacher_contacts.id'))
    notification_type = Column(String(50))  # 'OVERDUE', 'REMINDER'
    message = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)
    is_sent = Column(Boolean, default=False)
    
    student = relationship("Student")
    book = relationship("Book")
    teacher = relationship("TeacherContact")
# backend/services/notification_service.py
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from sqlalchemy import and_
from ..models.notification import Notification, TeacherContact
from ..models.student import BookTransaction

class NotificationService:
    def __init__(self, db_session):
        self.session = db_session
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.from_email = os.getenv('FROM_EMAIL')

    def check_overdue_books(self):
        """Check for overdue books and create notifications"""
        today = datetime.now().date()
        
        # Find overdue transactions
        overdue_transactions = self.session.query(BookTransaction).filter(
            and_(
                BookTransaction.due_date < today,
                BookTransaction.return_date.is_(None)
            )
        ).all()

        for transaction in overdue_transactions:
            # Get teacher contact for the student's class
            teacher = self.session.query(TeacherContact).filter_by(
                class_name=transaction.student.class_name,
                division=transaction.student.division,
                is_active=True
            ).first()

            if teacher:
                # Create notification
                message = self._create_overdue_message(transaction)
                notification = Notification(
                    student_id=transaction.student.id,
                    book_id=transaction.book_id,
                    teacher_id=teacher.id,
                    notification_type='OVERDUE',
                    message=message
                )
                self.session.add(notification)
        
        self.session.commit()

    def send_pending_notifications(self):
        """Send all pending notifications"""
        pending_notifications = self.session.query(Notification).filter_by(
            is_sent=False
        ).all()

        for notification in pending_notifications:
            if self._send_email_notification(notification):
                notification.sent_at = datetime.utcnow()
                notification.is_sent = True

        self.session.commit()

    def _create_overdue_message(self, transaction):
        days_overdue = (datetime.now().date() - transaction.due_date).days
        return f"""
        Student: {transaction.student.first_name} {transaction.student.last_name}
        Class: {transaction.student.class_name}-{transaction.student.division}
        Roll Number: {transaction.student.roll_number}
        Book: {transaction.book.title}
        Due Date: {transaction.due_date}
        Days Overdue: {days_overdue}
        """

    def _send_email_notification(self, notification):
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = notification.teacher.email
            msg['Subject'] = f"Library Notice: Overdue Book - Class {notification.student.class_name}-{notification.student.division}"

            body = f"""
            Dear {notification.teacher.name},

            This is to inform you about an overdue book in your class:

            {notification.message}

            Please remind the student to return the book as soon as possible.

            Best regards,
            Library Management System
            """

            msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            return True
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return False
# frontend/screens/notification_dashboard.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QTableWidget, QTableWidgetItem,
                           QLabel, QComboBox)
from PyQt6.QtCore import Qt, QTimer

class NotificationDashboard(QWidget):
    def __init__(self, notification_service):
        super().__init__()
        self.notification_service = notification_service
        self.init_ui()
        
        # Set up auto-refresh timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_notifications)
        self.timer.start(300000)  # Refresh every 5 minutes

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("Overdue Books Notifications")
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        # Filter section
        filter_layout = QHBoxLayout()
        self.class_combo = QComboBox()
        self.class_combo.addItems([str(i) for i in range(1, 13)])
        self.division_combo = QComboBox()
        self.division_combo.addItems(['All', 'A', 'B', 'C', 'D'])
        
        filter_layout.addWidget(QLabel("Class:"))
        filter_layout.addWidget(self.class_combo)
        filter_layout.addWidget(QLabel("Division:"))
        filter_layout.addWidget(self.division_combo)
        filter_layout.addStretch()
        
        # Notification table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Student Name", "Class", "Roll No", 
            "Book Title", "Days Overdue", "Status", "Action"
        ])
        
        # Buttons
        button_layout = QHBoxLayout()
        refresh_btn = QPushButton("Refresh")
        send_all_btn = QPushButton("Send All Notifications")
        
        refresh_btn.clicked.connect(self.refresh_notifications)
        send_all_btn.clicked.connect(self.send_all_notifications)
        
        button_layout.addWidget(refresh_btn)
        button_layout.addWidget(send_all_btn)
        
        # Add widgets to layout
        layout.addWidget(header)
        layout.addLayout(filter_layout)
        layout.addWidget(self.table)
        layout.addLayout(button_layout)

    def refresh_notifications(self):
        self.notification_service.check_overdue_books()
        self.load_notifications()

    def load_notifications(self):
        # Clear existing table
        self.table.setRowCount(0)
        
        # Get notifications based on filter
        class_name = self.class_combo.currentText()
        division = self.division_combo.currentText()
        
        # Load notifications from service
        notifications = self.get_filtered_notifications(class_name, division)
        
        for row, notif in enumerate(notifications):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(
                f"{notif.student.first_name} {notif.student.last_name}"))
            self.table.setItem(row, 1, QTableWidgetItem(
                f"{notif.student.class_name}-{notif.student.division}"))
            self.table.setItem(row, 2, QTableWidgetItem(
                str(notif.student.roll_number)))
            self.table.setItem(row, 3, QTableWidgetItem(
                notif.book.title))
            self.table.setItem(row, 4, QTableWidgetItem(
                str(self.calculate_days_overdue(notif))))
            
            status = "Sent" if notif.is_sent else "Pending"
            self.table.setItem(row, 5, QTableWidgetItem(status))
            
            # Add send button if notification is pending
            if not notif.is_sent:
                send_btn = QPushButton("Send")
                send_btn.clicked.connect(
                    lambda checked, n=notif: self.send_single_notification(n))
                self.table.setCellWidget(row, 6, send_btn)

    def send_single_notification(self, notification):
        if self.notification_service._send_email_notification(notification):
            self.refresh_notifications()

    def send_all_notifications(self):
        self.notification_service.send_pending_notifications()
        self.refresh_notifications()

    @staticmethod
    def calculate_days_overdue(notification):
        return (datetime.now().date() - notification.student.transactions[-1].due_date).days
# backend/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

class NotificationScheduler:
    def __init__(self, notification_service):
        self.notification_service = notification_service
        self.scheduler = BackgroundScheduler()

    def start(self):
        # Check for overdue books every morning at 8 AM
        self.scheduler.add_job(
            self.notification_service.check_overdue_books,
            trigger=CronTrigger(hour=8),
            id='check_overdue_books'
        )

        # Send pending notifications every hour
        self.scheduler.add_job(
            self.notification_service.send_pending_notifications,
            trigger=CronTrigger(minute=0),  # Every hour
            id='send_notifications'
        )

        self.scheduler.start()

    def stop(self):
        self.scheduler.shutdown()
# main.py
import os
from dotenv import load_dotenv
from backend.scheduler import NotificationScheduler
import backend.#!/usr/bin/env 
"""
Main entry point for the Library Management System.
Initializes core services and schedulers.
"""

# Standard library imports
import os
import sys
import logging
from typing import Optional

# Third-party imports
from dotenv import load_dotenv
from sqlalchemy.orm import Session

# Local application imports
from backend.scheduler import NotificationScheduler
from backend.services.notification_service import NotificationService
from backend.database import create_session  # Assuming you have this

def setup_logging() -> None:
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('library_system.log')
        ]
    )

def load_environment() -> bool:
    """
    Load environment variables from .env file.
    Returns: bool indicating success
    """
    try:
        load_dotenv()
        required_vars = [
            'SMTP_SERVER',
            'SMTP_PORT',
            'SMTP_USERNAME',
            'SMTP_PASSWORD',
            'FROM_EMAIL'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            logging.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            return False
            
        return True
    except Exception as e:
        logging.error(f"Failed to load environment variables: {e}")
        return False

def initialize_services(db_session: Session) -> Optional[tuple]:
    """
    Initialize core services required for the application.
    Returns: Tuple of (NotificationService, NotificationScheduler) or None if initialization fails
    """
    try:
        # Initialize notification service
        notification_service = NotificationService(db_session)
        
        # Initialize and start scheduler
        scheduler = NotificationScheduler(notification_service)
        
        return notification_service, scheduler
    except Exception as e:
        logging.error(f"Failed to initialize services: {e}")
        return None

def main() -> int:
    """
    Main function to start the application.
    Returns: Exit code (0 for success, 1 for failure)
    """
    # Setup logging first
    setup_logging()
    logging.info("Starting Library Management System")

    # Load environment variables
    if not load_environment():
        logging.error("Failed to load environment variables. Exiting.")
        return 1

    try:
        # Create database session
        db_session = create_session()
        
        # Initialize services
        services = initialize_services(db_session)
        if not services:
            logging.error("Failed to initialize services. Exiting.")
            return 1
            
        notification_service, scheduler = services
        
        # Start the scheduler
        scheduler.start()
        logging.info("Notification scheduler started successfully")

        # Keep the main thread alive
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            logging.info("Shutting down gracefully...")
            scheduler.stop()
            db_session.close()
            
        return 0

    except Exception as e:
        logging.error(f"Application failed to start: {e}")
        return 1
# Load environment variables
load_dotenv()

# Initialize notification service and scheduler
notification_service = NotificationService(db_session)
scheduler = NotificationScheduler(notification_service)
scheduler.start()
SMTP_SERVER= smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME= SMTP_USERNAME
SMTP_PASSWORD=your-app-specific-password
FROM_EMAIL= library@mailservice.com
