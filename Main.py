
import tkinter as tk
from tkinter import ttk
import numpy as np
import time
import random
import math


class TaskBasedAnalyzer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Parkinson's Disease Detection")
        self.root.geometry("1000x800")

        # Task variables
        self.movements = []
        self.start_time = None
        self.is_recording = False
        self.is_drawing = False
        self.current_task = None
        self.target_points = []
        self.target_click_times = []  # Will store reaction times, not timestamps
        self.targets_clicked = 0

        # Target variables
        self.target_id = None
        self.target_move_job = None
        self.target_timeout_job = None
        self.target_dx = 0
        self.target_dy = 0
        self.target_missed = 0
        self.target_speed = 2  # Speed of target movement
        self.target_timeout = 3000  # Time in ms before target disappears if not clicked
        self.target_appear_time = None  # When target appears
        self.target_radius = 25  # Size of target (larger for easier clicking)

        # Results storage
        self.results = {
            "line": {"mse": None, "time_taken": None, "smoothness": None},
            "square": {"mse": None, "time_taken": None, "smoothness": None},
            "target": {"avg_time": None, "std_dev": None, "missed": None}
        }

        # Available tests
        self.tests = ["line", "square", "target"]

        # Food recommendations based on risk level
        self.food_recommendations = {
            "low": [
                "Berries (blueberries, strawberries) - high in antioxidants",
                "Green tea - contains polyphenols",
                "Nuts (walnuts, almonds) - good source of healthy fats",
                "Fatty fish (salmon, mackerel) - rich in omega-3 fatty acids",
                "Turmeric - contains curcumin with anti-inflammatory properties"
            ],
            "moderate": [
                "Green leafy vegetables (spinach, kale) - high in antioxidants",
                "Probiotic foods (yogurt, kefir) - supports gut-brain axis",
                "Olive oil - contains oleocanthal with anti-inflammatory properties",
                "Whole grains - provides sustained energy and fiber",
                "Fresh herbs (rosemary, oregano) - contains antioxidants",
                "Water with lemon - helps with hydration and detoxification"
            ],
            "high": [
                "Fresh vegetables (broccoli, bell peppers) - high in antioxidants",
                "Legumes (lentils, beans) - rich in protein and fiber",
                "Fermented foods (sauerkraut, kimchi) - supports gut health",
                "Seeds (flaxseeds, chia seeds) - high in omega-3 fatty acids",
                "Dark chocolate (70%+ cocoa) - contains flavonoids",
                "Ginger - has anti-inflammatory properties",
                "Green smoothies - easy to digest nutrients",
                "Hydrating foods (cucumber, watermelon)"
            ]
        }

        # Create UI elements
        self.setup_frames()
        self.setup_task_buttons()
        self.setup_canvas()
        self.setup_results_display()

    def setup_task_buttons(self):
        # Individual test buttons
        self.test_buttons_frame = ttk.LabelFrame(self.control_frame, text="Available Tests")
        self.test_buttons_frame.pack(pady=10, fill='x')

        self.line_test_btn = ttk.Button(self.test_buttons_frame, text="1. Follow Line Test",
                                        command=lambda: self.start_specific_test("line"))
        self.line_test_btn.pack(pady=5, fill='x')

        self.square_test_btn = ttk.Button(self.test_buttons_frame, text="2. Draw Square Test",
                                          command=lambda: self.start_specific_test("square"))
        self.square_test_btn.pack(pady=5, fill='x')

        self.target_test_btn = ttk.Button(self.test_buttons_frame, text="3. Click Targets Test",
                                          command=lambda: self.start_specific_test("target"))
        self.target_test_btn.pack(pady=5, fill='x')

        # Other control buttons
        self.clear_btn = ttk.Button(self.control_frame, text="Clear Canvas", command=self.clear_canvas)
        self.clear_btn.pack(pady=10, fill='x')

        self.show_results_btn = ttk.Button(self.control_frame, text="Show Final Diagnosis",
                                           command=self.display_final_diagnosis)
        self.show_results_btn.pack(pady=20, fill='x')

        # Status indicators
        self.status_frame = ttk.LabelFrame(self.control_frame, text="Test Status")
        self.status_frame.pack(pady=10, fill='x')

        self.line_status = ttk.Label(self.status_frame, text="Line Test: Not Started")
        self.line_status.pack(pady=2, anchor='w')

        self.square_status = ttk.Label(self.status_frame, text="Square Test: Not Started")
        self.square_status.pack(pady=2, anchor='w')

        self.target_status = ttk.Label(self.status_frame, text="Target Test: Not Started")
        self.target_status.pack(pady=2, anchor='w')

        # Add difficulty slider for target test
        self.difficulty_frame = ttk.LabelFrame(self.control_frame, text="Target Test Settings")
        self.difficulty_frame.pack(pady=10, fill='x')

        ttk.Label(self.difficulty_frame, text="Speed:").pack(anchor='w')
        self.speed_slider = ttk.Scale(self.difficulty_frame, from_=1, to=5, orient='horizontal')
        self.speed_slider.set(2)  # Default speed
        self.speed_slider.pack(fill='x')

        ttk.Label(self.difficulty_frame, text="Timeout (sec):").pack(anchor='w')
        self.timeout_slider = ttk.Scale(self.difficulty_frame, from_=1, to=5, orient='horizontal')
        self.timeout_slider.set(3)  # Default timeout
        self.timeout_slider.pack(fill='x')

        # Debug info
        self.debug_var = tk.BooleanVar(value=False)
        self.debug_checkbox = ttk.Checkbutton(self.control_frame, text="Show Debug Info",
                                              variable=self.debug_var)
        self.debug_checkbox.pack(pady=5)

        self.debug_frame = ttk.Frame(self.control_frame)
        self.debug_frame.pack(fill='x', pady=5)

        self.debug_label = ttk.Label(self.debug_frame, text="Debug Info: None", wraplength=180)
        self.debug_label.pack(pady=5, fill='both', expand=True)

    def setup_frames(self):
        self.control_frame = ttk.Frame(self.root, width=200)
        self.control_frame.pack(side='left', padx=10, pady=10, fill='y')
        self.control_frame.pack_propagate(False)  # Prevent resizing based on content

        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(side='right', expand=True, fill='both', padx=10, pady=10)

        self.results_frame = ttk.Frame(self.main_frame)
        self.results_frame.pack(side='bottom', fill='x', pady=10)

    def setup_canvas(self):
        self.canvas_frame = ttk.Frame(self.main_frame)
        self.canvas_frame.pack(expand=True, fill='both')

        self.canvas = tk.Canvas(self.canvas_frame, bg='white')
        self.canvas.pack(expand=True, fill='both')

        # Set minimum size for canvas to prevent shrinking
        self.canvas.config(width=800, height=800)

        # Only use essential bindings to avoid conflict
        self.canvas.bind('<Motion>', self.on_mouse_move)
        self.canvas.bind('<ButtonPress-1>', self.on_mouse_down)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_up)

        # Separate click handler specifically for targets
        self.canvas.bind('<Button-1>', self.on_target_click, add="+")  # Use add='+' to avoid overriding

    def setup_results_display(self):
        # Create frame for results with potential scrolling
        self.result_display_frame = ttk.Frame(self.results_frame)
        self.result_display_frame.pack(fill='both', expand=True)

        self.result_label = ttk.Label(self.result_display_frame, text="Select a test to begin",
                                      font=('Arial', 12), wraplength=700)
        self.result_label.pack(pady=5)

    def clear_canvas(self):
        self.canvas.delete("all")
        self.movements = []
        self.target_points = []
        self.target_click_times = []
        self.targets_clicked = 0
        self.target_missed = 0
        self.target_appear_time = None

        # Cancel any scheduled jobs
        if self.target_move_job:
            self.root.after_cancel(self.target_move_job)
            self.target_move_job = None
        if self.target_timeout_job:
            self.root.after_cancel(self.target_timeout_job)
            self.target_timeout_job = None

        self.result_label.config(text="Select a test to begin")
        self.current_task = None
        self.is_drawing = False
        self.debug_label.config(text="Debug Info: None")

    def start_specific_test(self, test_name):
        """Start a specific test selected by the user"""
        self.clear_canvas()
        self.current_task = test_name

        if test_name == "line":
            self.start_line_task()
        elif test_name == "square":
            self.start_square_task()
        elif test_name == "target":
            self.start_target_task()

    def start_line_task(self):
        """Initialize the Follow Line task"""
        self.result_label.config(text="Follow Line Task: Click and hold to draw along the line.")
        self.line_status.config(text="Line Test: In Progress")
        self.root.update()

        width, height = 800, 600
        self.canvas.create_line(100, height // 2, 700, height // 2, fill='gray', dash=(5, 5), width=20)
        self.movements = []
        self.start_time = time.time()
        self.is_recording = True
        self.is_drawing = False

        # Add instruction text
        self.canvas.create_text(400, 150, text="Click and hold mouse button to draw", fill="gray", font=('Arial', 12))

    def start_square_task(self):
        """Initialize the Draw Square task"""
        self.result_label.config(text="Draw Square Task: Click and hold to draw the square.")
        self.square_status.config(text="Square Test: In Progress")
        self.root.update()

        center_x, center_y = 400, 300
        side_length = 160
        line_width = 20

        # Calculate the square corners
        x1 = center_x - side_length / 2
        y1 = center_y - side_length / 2
        x2 = center_x + side_length / 2
        y2 = center_y + side_length / 2

        # Create square outline
        self.canvas.create_rectangle(x1, y1, x2, y2, outline='gray', dash=(5, 5), width=line_width)
        self.movements = []
        self.start_time = time.time()
        self.is_recording = True
        self.is_drawing = False

        # Add instruction text
        self.canvas.create_text(400, 150, text="Click and hold mouse button to draw", fill="gray", font=('Arial', 12))

    def start_target_task(self):
        """Initialize the Click Targets task with moving targets"""
        self.result_label.config(text="Click Targets Task: Click on each moving target as quickly as possible.")
        self.target_status.config(text="Target Test: In Progress")
        self.target_speed = self.speed_slider.get()
        self.target_timeout = int(self.timeout_slider.get() * 1000)  # Convert to milliseconds
        self.root.update()

        self.targets_clicked = 0
        self.target_missed = 0
        self.target_points = []
        self.target_click_times = []  # This will store reaction times
        self.start_time = time.time()

        # Show instructions
        self.canvas.create_text(400, 100, text="Click on each moving target as quickly as you can",
                                fill="black", font=('Arial', 14), tags="instruction")
        self.canvas.create_text(400, 130, text="Targets will disappear if not clicked in time",
                                fill="black", font=('Arial', 12), tags="instruction")

        # Create first target
        self.root.after(500, self.create_new_target)  # Small delay to allow UI to update

    def create_new_target(self):
        """Creates a new random moving target until 5 targets are clicked or missed"""
        # First clear any miss markers from previous target
        self.canvas.delete('miss_marker')

        if self.targets_clicked + self.target_missed >= 5:
            self.analyze_target_task()
            return

        # Cancel any existing target movement jobs
        if self.target_move_job:
            self.root.after_cancel(self.target_move_job)
            self.target_move_job = None
        if self.target_timeout_job:
            self.root.after_cancel(self.target_timeout_job)
            self.target_timeout_job = None

        # Get canvas dimensions
        canvas_width = self.canvas.winfo_width() or 800
        canvas_height = self.canvas.winfo_height() or 600

        # Generate random position with padding
        x = random.randint(50, canvas_width - 50)
        y = random.randint(150, canvas_height - 150)

        # Random direction for movement
        self.target_dx = random.choice([-1, 1]) * self.target_speed
        self.target_dy = random.choice([-1, 1]) * self.target_speed

        # Create target
        self.target_id = self.canvas.create_oval(
            x - self.target_radius, y - self.target_radius,
            x + self.target_radius, y + self.target_radius,
            fill='red', tags='target', outline='black', width=2
        )

        # Store target center position
        target_center = (x, y)
        self.target_points.append(target_center)

        # Debug info
        if self.debug_var.get():
            self.debug_label.config(text=f"Target created at: \n{target_center}")

        # Record the time the target appears
        self.target_appear_time = time.time()

        # Show target counter
        self.canvas.delete('counter')
        self.canvas.create_text(400, 70, text=f"Target {self.targets_clicked + self.target_missed + 1} of 5",
                                fill="black", font=('Arial', 12), tags='counter')

        # Start moving the target
        self.move_target()

        # Set timeout for target if not clicked
        self.target_timeout_job = self.root.after(self.target_timeout, self.target_timeout_handler)

    def move_target(self):
        """Move the target around the canvas"""
        if not self.target_id or self.current_task != "target":
            return

        # Get current position
        try:
            coords = self.canvas.coords(self.target_id)
            if not coords:  # Target was already removed
                return
        except tk.TclError:
            return  # Canvas or target no longer exists

        x1, y1, x2, y2 = coords
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()

        # Default if dimensions not yet set
        if width <= 1:
            width = 800
        if height <= 1:
            height = 600

        # Bounce off edges
        if x1 <= 0 or x2 >= width:
            self.target_dx *= -1
        if y1 <= 0 or y2 >= height:
            self.target_dy *= -1

        # Move target
        self.canvas.move(self.target_id, self.target_dx, self.target_dy)

        # Schedule next movement
        self.target_move_job = self.root.after(20, self.move_target)  # Move every 20ms

    def target_timeout_handler(self):
        """Handle timeout when target is not clicked in time"""
        if not self.target_id:
            return

        try:
            # Mark this target as missed
            self.target_missed += 1

            # Flash the target to indicate it was missed
            self.canvas.itemconfig(self.target_id, fill='gray')

            # Debug info
            if self.debug_var.get():
                self.debug_label.config(text=f"Target timed out. \nTotal missed: {self.target_missed}")

            self.root.after(500, self.after_missed_target)
        except tk.TclError:
            # Target might have been deleted
            self.after_missed_target()

    def after_missed_target(self):
        """Clean up after missing a target and create a new one"""
        self.canvas.delete('target')
        self.target_id = None

        # Create next target
        self.create_new_target()

    def on_mouse_down(self, event):
        """Handle mouse button press events for drawing tasks"""
        if self.is_recording and self.current_task in ["square", "line"]:
            self.is_drawing = True
            self.movements.append([event.x, event.y, time.time() - self.start_time])

    def on_mouse_up(self, event):
        """Handle mouse button release events"""
        if self.is_recording and self.current_task in ["square", "line"]:
            self.is_drawing = False
            self.analyze_current_task()  # Analyze the task when the user releases the mouse button

    def on_mouse_move(self, event):
        """Handle mouse movement events - only record if mouse button is pressed"""
        if self.is_recording and self.current_task in ["square", "line"] and self.is_drawing:
            self.movements.append([event.x, event.y, time.time() - self.start_time])
            if len(self.movements) > 1:
                prev = self.movements[-2]
                self.canvas.create_line(prev[0], prev[1], event.x, event.y, fill='blue', width=2)

    def on_target_click(self, event):
        """Dedicated handler for clicking targets"""
        if self.current_task != "target" or not self.target_id:
            return

        # Show where user clicked (debug)
        if self.debug_var.get():
            self.canvas.create_oval(event.x - 3, event.y - 3, event.x + 3, event.y + 3,
                                    fill='yellow', outline='black', tags='click_marker')
            self.root.after(500, lambda: self.canvas.delete('click_marker'))

        try:
            # Get target coordinates
            target_coords = self.canvas.coords(self.target_id)

            if not target_coords or not self.target_appear_time:
                return

            x1, y1, x2, y2 = target_coords
            target_x = (x1 + x2) / 2
            target_y = (y1 + y2) / 2

            # Calculate distance from click to target center
            distance = math.sqrt((event.x - target_x) ** 2 + (event.y - target_y) ** 2)

            # Debug info
            if self.debug_var.get():
                self.debug_label.config(
                    text=f"Click at ({event.x}, {event.y}), \nTarget at ({target_x:.1f}, {target_y:.1f}), "
                         f"Distance: {distance:.1f}, \nRadius: {self.target_radius}")

            # Hit detection - slightly larger than visual radius for better UX
            if distance <= self.target_radius + 5:  # 5px grace margin
                # Success - calculate reaction time
                click_time = time.time() - self.target_appear_time
                self.target_click_times.append(click_time)
                self.targets_clicked += 1

                # Cancel timeout
                if self.target_timeout_job:
                    self.root.after_cancel(self.target_timeout_job)
                    self.target_timeout_job = None

                # Visual feedback
                self.canvas.itemconfig(self.target_id, fill='green')
                self.canvas.create_text(target_x, target_y, text=f"{click_time:.2f}s",
                                        tags="hit_time", font=('Arial', 10, 'bold'))

                # Debug info
                if self.debug_var.get():
                    self.debug_label.config(
                        text=f"Target hit! \nTime: {click_time:.2f}s, \nTotal hits: {self.targets_clicked}")

                # Schedule cleanup and next target
                self.target_id = None  # Prevent double-click issues
                self.root.after(800, self.clear_hit_animation)
            else:
                # User clicked but missed the target
                self.target_missed += 1

                # Visual feedback for miss
                miss_marker = self.canvas.create_oval(
                    event.x - 5, event.y - 5, event.x + 5, event.y + 5,
                    fill='red', outline='black', tags='miss_marker'
                )
                self.canvas.create_line(
                    event.x, event.y, target_x, target_y,
                    fill='red', dash=(2, 2), tags='miss_marker'
                )

                # Debug info
                if self.debug_var.get():
                    self.debug_label.config(
                        text=f"Target missed! \nDistance: {distance:.2f}px, \nTotal misses: {self.target_missed}")

                # Clear miss marker after a short delay
                self.root.after(500, lambda: self.canvas.delete('miss_marker'))

        except tk.TclError:
            # Handle case where target was removed
            pass

    def clear_hit_animation(self):
        """Clear hit animation and time display"""
        self.canvas.delete('target')
        self.canvas.delete('hit_time')
        self.canvas.delete('miss_marker')  # Clear any miss markers

        # Create next target
        self.create_new_target()

    def analyze_current_task(self):
        """Analyze the current task based on its type"""
        if self.current_task == "line":
            self.analyze_line_task()
        elif self.current_task == "square":
            self.analyze_square_task()

    def analyze_line_task(self):
        """Analyze the Follow Line task"""
        if len(self.movements) < 3:
            self.line_status.config(text="Line Test: Invalid (too few points)")
            return

        # Target horizontal line is at height/2 (300)
        y_target = 300

        # Calculate distances from each point to the target line
        distances = [abs(y - y_target) for _, y, _ in self.movements]

        # Calculate mean squared error
        mse = np.mean([d ** 2 for d in distances])

        # Calculate smoothness using the new method
        smoothness = self.calculate_smoothness(self.movements)

        # Calculate time taken to complete the task
        time_taken = self.movements[-1][2] - self.movements[0][2]

        # Store results
        self.results["line"]["mse"] = mse
        self.results["line"]["time_taken"] = time_taken
        self.results["line"]["smoothness"] = smoothness

        # Display results
        self.result_label.config(
            text=f"Line Task Complete\nDeviation: {mse:.2f}\nTime Taken: {time_taken:.2f} sec\nSmoothness: {smoothness:.2f}/10")
        self.line_status.config(text="Line Test: Completed ✓")

    def analyze_square_task(self):
        """Analyze the Draw Square task"""
        if len(self.movements) < 3:
            self.square_status.config(text="Square Test: Invalid (too few points)")
            return

        center_x, center_y = 400, 300
        side_length = 160

        # Calculate the square corners
        x1 = center_x - side_length / 2
        y1 = center_y - side_length / 2
        x2 = center_x + side_length / 2
        y2 = center_y + side_length / 2

        # Calculate deviation from the square edges
        distances = []
        for x, y, _ in self.movements:
            # Distance calculations to each edge (when within the x/y bounds of that edge)
            dist_left = abs(x - x1) if y1 <= y <= y2 else float('inf')
            dist_right = abs(x - x2) if y1 <= y <= y2 else float('inf')
            dist_top = abs(y - y1) if x1 <= x <= x2 else float('inf')
            dist_bottom = abs(y - y2) if x1 <= x <= x2 else float('inf')

            # Distance to corners (Pythagorean theorem)
            dist_top_left = math.sqrt((x - x1) ** 2 + (y - y1) ** 2)
            dist_top_right = math.sqrt((x - x2) ** 2 + (y - y1) ** 2)
            dist_bottom_left = math.sqrt((x - x1) ** 2 + (y - y2) ** 2)
            dist_bottom_right = math.sqrt((x - x2) ** 2 + (y - y2) ** 2)

            # Find the minimum distance
            min_dist = min(
                dist_left, dist_right, dist_top, dist_bottom,
                dist_top_left, dist_top_right, dist_bottom_left, dist_bottom_right
            )

            distances.append(min_dist)

        # Calculate mean squared error
        mse = np.mean([d ** 2 for d in distances])

        # Calculate smoothness using the new method
        smoothness = self.calculate_smoothness(self.movements)

        # Calculate time taken to complete the task
        time_taken = self.movements[-1][2] - self.movements[0][2]

        # Store results
        self.results["square"]["mse"] = mse
        self.results["square"]["time_taken"] = time_taken
        self.results["square"]["smoothness"] = smoothness

        # Display results
        self.result_label.config(
            text=f"Square Task Complete\nDeviation: {mse:.2f}\nTime Taken: {time_taken:.2f} sec\nSmoothness: {smoothness:.2f}/10")
        self.square_status.config(text="Square Test: Completed ✓")

    def calculate_smoothness(self, movements):
        """Calculate drawing smoothness based on velocity changes"""
        if len(movements) < 3:
            return 5.0  # Default value for very few points

        # Calculate velocities
        velocities = []
        for i in range(1, len(movements)):
            x1, y1, t1 = movements[i - 1]
            x2, y2, t2 = movements[i]

            # Skip if time difference is too small
            if abs(t2 - t1) < 0.001:
                continue

            # Calculate velocity (distance/time)
            distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            velocity = distance / (t2 - t1)
            velocities.append(velocity)

        if len(velocities) < 2:
            return 5.0

        # Calculate acceleration (changes in velocity)
        accelerations = [abs(velocities[i] - velocities[i - 1]) for i in range(1, len(velocities))]

        # Calculate normalized jerk (rate of change of acceleration)
        # Lower jerk indicates smoother movement
        if len(accelerations) < 2:
            mean_jerk = 0
        else:
            jerks = [abs(accelerations[i] - accelerations[i - 1]) for i in range(1, len(accelerations))]
            mean_jerk = np.mean(jerks) if jerks else 0

        # Normalize jerk to a 0-10 scale (inverted so higher is smoother)
        # Using exponential decay function to map jerk to smoothness
        smoothness = 10 * math.exp(-mean_jerk / 50)

        # Ensure bounds
        return max(0, min(10, smoothness))


    def analyze_target_task(self):
        """Analyze the Click Targets task"""
        # Cancel any active target jobs
        if self.target_move_job:
            self.root.after_cancel(self.target_move_job)
            self.target_move_job = None
        if self.target_timeout_job:
            self.root.after_cancel(self.target_timeout_job)
            self.target_timeout_job = None

        # Clear canvas elements related to target task
        self.canvas.delete('target')
        self.canvas.delete('counter')
        self.canvas.delete('hit_time')
        self.canvas.delete('instruction')

        # Check if we have valid click times
        if not self.target_click_times:
            self.target_status.config(text="Target Test: Invalid (no successful clicks)")
            self.result_label.config(text="Target Task: No successful clicks recorded")
            return

        # Calculate the average reaction time
        avg_time = np.mean(self.target_click_times)

        # Calculate standard deviation
        std_dev = np.std(self.target_click_times) if len(self.target_click_times) > 1 else 0

        # Store results
        self.results["target"]["avg_time"] = avg_time
        self.results["target"]["std_dev"] = std_dev
        self.results["target"]["missed"] = self.target_missed
        result_text = (f"Target Task Complete\n"
                       f"Targets Hit: {self.targets_clicked} / Missed: {self.target_missed}\n"
                       f"Average Reaction Time: {avg_time:.2f} sec\n"
                       f"Consistency (StdDev): {std_dev:.2f} sec")

        self.result_label.config(text=result_text)
        self.target_status.config(text="Target Test: Completed ✓")

    def display_final_diagnosis(self):
        """Display final diagnosis based on all test results"""
        # Check if all tests have been completed
        if any(self.results[test][key] is None for test in self.tests for key in self.results[test]):
            incomplete_tests = []
            if self.results["line"]["mse"] is None:
                incomplete_tests.append("Line")
            if self.results["square"]["mse"] is None:
                incomplete_tests.append("Square")
            if self.results["target"]["avg_time"] is None:
                incomplete_tests.append("Target")

            self.result_label.config(
                text=f"Please complete all tests before diagnosis.\nIncomplete tests: {', '.join(incomplete_tests)}")
            return

        # Calculate overall risk score
        risk_score = self.calculate_risk_score()

        # Determine risk level
        if risk_score < 3:
            risk_level = "Low"
            color = "green"
        elif risk_score < 6:
            risk_level = "Moderate"
            color = "orange"
        else:
            risk_level = "High"
            color = "red"

        # Get recommended foods based on risk level
        food_recs = self.food_recommendations[risk_level.lower()]

        # Create a formatted list of food recommendations
        food_text = "\n".join([f"• {food}" for food in food_recs[:5]])

        # Display comprehensive results
        diagnosis_text = (
            f"PARKINSON'S RISK ASSESSMENT\n\n"
            f"Overall Risk Level: {risk_level} (Score: {risk_score:.1f}/10)\n\n"
            f"Line Test Results:\n"
            f"  - Deviation from Path: {self.results['line']['mse']:.1f} px²\n"
            f"  - Drawing Smoothness: {self.results['line']['smoothness']:.1f}/10\n"
            f"  - Completion Time: {self.results['line']['time_taken']:.1f} sec\n\n"
            f"Square Test Results:\n"
            f"  - Deviation from Path: {self.results['square']['mse']:.1f} px²\n"
            f"  - Drawing Smoothness: {self.results['square']['smoothness']:.1f}/10\n"
            f"  - Completion Time: {self.results['square']['time_taken']:.1f} sec\n\n"
            f"Target Test Results:\n"
            f"  - Average Reaction Time: {self.results['target']['avg_time']:.2f} sec\n"
            f"  - Consistency (StdDev): {self.results['target']['std_dev']:.2f} sec\n"
            f"  - Targets Missed: {self.results['target']['missed']}\n\n"
            f"Recommended Foods for {risk_level} Risk:\n{food_text}\n\n"
            f"DISCLAIMER: This is not a medical diagnosis. Please consult with a healthcare professional for proper evaluation."
        )

        self.result_label.config(text=diagnosis_text, foreground=color)

        # Clear canvas and show visualization of results
        self.canvas.delete("all")
        self.visualize_results()

    def calculate_risk_score(self):
        """Calculate overall risk score from all test results"""
        # Line test score (higher MSE and lower smoothness increase risk)
        line_mse_score = min(5, self.results["line"]["mse"] / 100)
        line_smoothness_score = max(0, 5 - self.results["line"]["smoothness"] / 2)

        # Square test score (higher MSE and lower smoothness increase risk)
        square_mse_score = min(5, self.results["square"]["mse"] / 100)
        square_smoothness_score = max(0, 5 - self.results["square"]["smoothness"] / 2)

        # Target test score (higher reaction time and more misses increase risk)
        target_time_score = min(5, self.results["target"]["avg_time"] * 2)
        target_miss_score = min(5, self.results["target"]["missed"])

        # Combine scores with different weights
        line_score = (line_mse_score * 0.6) + (line_smoothness_score * 0.4)
        square_score = (square_mse_score * 0.6) + (square_smoothness_score * 0.4)
        target_score = (target_time_score * 0.7) + (target_miss_score * 0.3)

        # Overall score (weighted average)
        overall_score = (line_score * 0.35) + (square_score * 0.35) + (target_score * 0.3)

        # Scale to 0-10
        return min(10, overall_score * 2)

    def visualize_results(self):
        """Create visualization of test results"""
        width, height = 800, 600

        # Draw title
        self.canvas.create_text(400, 50, text="TEST RESULTS VISUALIZATION",
                                font=('Arial', 16, 'bold'))

        # Draw line test visualization
        self.canvas.create_text(200, 100, text="Line Test", font=('Arial', 12, 'bold'))

        # Line deviation indicator
        norm_deviation = min(1.0, self.results["line"]["mse"] / 200)
        deviation_width = norm_deviation * 200
        self.canvas.create_rectangle(100, 170, 300, 190, fill='lightgray', outline='gray')
        self.canvas.create_rectangle(100, 170, 100 + deviation_width, 190, fill='red', outline='')
        self.canvas.create_text(200, 200, text=f"Deviation: {self.results['line']['mse']:.1f} px²")

        # Draw square test visualization
        self.canvas.create_text(600, 100, text="Square Test", font=('Arial', 12, 'bold'))

        # Square deviation indicator
        norm_deviation = min(1.0, self.results["square"]["mse"] / 200)
        deviation_width = norm_deviation * 200
        self.canvas.create_rectangle(500, 170, 700, 190, fill='lightgray', outline='gray')
        self.canvas.create_rectangle(500, 170, 500 + deviation_width, 190, fill='red', outline='')
        self.canvas.create_text(600, 200, text=f"Deviation: {self.results['square']['mse']:.1f} px²")

        # Draw target test visualization
        self.canvas.create_text(400, 250, text="Target Test", font=('Arial', 12, 'bold'))

        # Target accuracy indicator
        total_targets = self.targets_clicked + self.target_missed
        if total_targets > 0:
            accuracy = self.targets_clicked / total_targets
        else:
            accuracy = 0

        self.canvas.create_oval(350, 270, 450, 370, outline='gray', width=2)
        self.canvas.create_arc(350, 270, 450, 370, start=90, extent=360 * accuracy,
                               fill='green', outline='')
        self.canvas.create_text(400, 320, text=f"{accuracy * 100:.0f}%", font=('Arial', 12, 'bold'))
        self.canvas.create_text(400, 380, text=f"Accuracy: {self.targets_clicked}/{total_targets} targets")

        # Reaction time indicator
        self.canvas.create_text(400, 410, text=f"Avg Reaction: {self.results['target']['avg_time']:.2f}s")

        # Draw overall risk score
        risk_score = self.calculate_risk_score()

        # Determine risk level and color
        if risk_score < 3:
            risk_level = "LOW RISK"
            color = "green"
        elif risk_score < 6:
            risk_level = "MODERATE RISK"
            color = "orange"
        else:
            risk_level = "HIGH RISK"
            color = "red"

        # Draw semicircular risk meter
        center_x, center_y = 400, 500
        radius = 150

        # Draw the background semicircle
        self.canvas.create_arc(center_x - radius, center_y - radius,
                               center_x + radius, center_y + radius,
                               start=180, extent=180, fill='lightgray', outline='gray')

        # Draw the colored risk indicator
        risk_angle = 180 * (risk_score / 10)
        self.canvas.create_arc(center_x - radius, center_y - radius,
                               center_x + radius, center_y + radius,
                               start=180, extent=risk_angle, fill=color, outline='')

        # Draw risk score text
        self.canvas.create_text(center_x, center_y - 30, text=f"{risk_level}",
                                font=('Arial', 16, 'bold'), fill=color)
        self.canvas.create_text(center_x, center_y, text=f"Score: {risk_score:.1f}/10",
                                font=('Arial', 12), fill=color)

    def run(self):
        """Start the main application loop"""
        self.root.mainloop()


if __name__ == "__main__":
    app = TaskBasedAnalyzer()
    app.run()
