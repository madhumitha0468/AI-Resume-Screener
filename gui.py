import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import csv
import resume_screener


class ResumeScreenerGUI:

    def __init__(self, root):
        self.root = root

        # =========================
        # WINDOW
        # =========================

        self.root.title("AI Resume Screening System")
        self.root.geometry("1150x760")
        self.root.minsize(1000, 650)

        # =========================
        # COLORS
        # =========================

        self.bg = "#F4F7FB"
        self.card = "#FFFFFF"
        self.primary = "#2563EB"
        self.primary_dark = "#1D4ED8"
        self.success = "#16A34A"
        self.text = "#1E293B"
        self.muted = "#64748B"
        self.border = "#E2E8F0"
        self.warning = "#F59E0B"

        self.root.configure(bg=self.bg)

        # =========================
        # VARIABLES
        # =========================

        self.jd_path = ""
        self.resume_folder = ""
        self.results = []
        self.keywords = []

        # =========================
        # STYLE
        # =========================

        self.setup_styles()

        # =========================
        # HEADER
        # =========================

        header = tk.Frame(
            root,
            bg=self.primary,
            height=110
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        title = tk.Label(
            header,
            text="AI RESUME SCREENING SYSTEM",
            bg=self.primary,
            fg="white",
            font=("Segoe UI", 25, "bold")
        )
        title.pack(pady=(22, 2))

        subtitle = tk.Label(
            header,
            text="Intelligent Resume • Job Description Matching • Candidate Ranking",
            bg=self.primary,
            fg="#DBEAFE",
            font=("Segoe UI", 11)
        )
        subtitle.pack()

        # =========================
        # MAIN CONTAINER
        # =========================

        main = tk.Frame(
            root,
            bg=self.bg
        )
        main.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=25
        )

        # =========================
        # INPUT CARD
        # =========================

        input_card = tk.Frame(
            main,
            bg=self.card,
            highlightbackground=self.border,
            highlightthickness=1
        )
        input_card.pack(fill="x", pady=(0, 18))

        tk.Label(
            input_card,
            text="📂  INPUT DOCUMENTS",
            bg=self.card,
            fg=self.text,
            font=("Segoe UI", 13, "bold")
        ).grid(
            row=0,
            column=0,
            columnspan=3,
            sticky="w",
            padx=20,
            pady=(18, 12)
        )

        # JD label

        tk.Label(
            input_card,
            text="Job Description",
            bg=self.card,
            fg=self.text,
            font=("Segoe UI", 10, "bold")
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=(20, 10),
            pady=8
        )

        self.jd_label = tk.Label(
            input_card,
            text="No Job Description selected",
            bg="#F8FAFC",
            fg=self.muted,
            anchor="w",
            font=("Segoe UI", 10),
            relief="flat"
        )
        self.jd_label.grid(
            row=1,
            column=1,
            sticky="ew",
            padx=10,
            pady=8,
            ipady=7
        )

        self.jd_button = tk.Button(
            input_card,
            text="Browse JD",
            command=self.select_jd,
            bg=self.primary,
            fg="white",
            activebackground=self.primary_dark,
            activeforeground="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            padx=18,
            pady=7
        )
        self.jd_button.grid(
            row=1,
            column=2,
            padx=(10, 20),
            pady=8
        )

        # Resume folder

        tk.Label(
            input_card,
            text="Resume Folder",
            bg=self.card,
            fg=self.text,
            font=("Segoe UI", 10, "bold")
        ).grid(
            row=2,
            column=0,
            sticky="w",
            padx=(20, 10),
            pady=(8, 18)
        )

        self.resume_label = tk.Label(
            input_card,
            text="No resume folder selected",
            bg="#F8FAFC",
            fg=self.muted,
            anchor="w",
            font=("Segoe UI", 10)
        )
        self.resume_label.grid(
            row=2,
            column=1,
            sticky="ew",
            padx=10,
            pady=(8, 18),
            ipady=7
        )

        self.folder_button = tk.Button(
            input_card,
            text="Browse Folder",
            command=self.select_resume_folder,
            bg=self.primary,
            fg="white",
            activebackground=self.primary_dark,
            activeforeground="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            padx=18,
            pady=7
        )
        self.folder_button.grid(
            row=2,
            column=2,
            padx=(10, 20),
            pady=(8, 18)
        )

        input_card.columnconfigure(1, weight=1)

        # =========================
        # ACTION BUTTONS
        # =========================

        action_frame = tk.Frame(
            main,
            bg=self.bg
        )
        action_frame.pack(fill="x", pady=(0, 18))

        self.screen_button = tk.Button(
            action_frame,
            text="🔍  SCREEN RESUMES",
            command=self.screen_resumes,
            bg=self.success,
            fg="white",
            activebackground="#15803D",
            activeforeground="white",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            cursor="hand2",
            padx=24,
            pady=10
        )
        self.screen_button.pack(side="left", padx=(0, 10))

        self.export_button = tk.Button(
            action_frame,
            text="📊  EXPORT CSV",
            command=self.export_csv,
            bg=self.primary,
            fg="white",
            activebackground=self.primary_dark,
            activeforeground="white",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=10
        )
        self.export_button.pack(side="left", padx=10)

        self.clear_button = tk.Button(
            action_frame,
            text="✕  CLEAR",
            command=self.clear_results,
            bg="#E2E8F0",
            fg=self.text,
            activebackground="#CBD5E1",
            activeforeground=self.text,
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=10
        )
        self.clear_button.pack(side="left", padx=10)

        # =========================
        # TOP CANDIDATE CARD
        # =========================

        top_card = tk.Frame(
            main,
            bg="#ECFDF5",
            highlightbackground="#BBF7D0",
            highlightthickness=1
        )
        top_card.pack(fill="x", pady=(0, 18))

        self.top_candidate = tk.Label(
            top_card,
            text="🏆  Top Candidate: Not available",
            bg="#ECFDF5",
            fg="#166534",
            font=("Segoe UI", 14, "bold"),
            anchor="w"
        )
        self.top_candidate.pack(
            fill="x",
            padx=20,
            pady=14
        )

        # =========================
        # RESULTS CARD
        # =========================

        result_card = tk.Frame(
            main,
            bg=self.card,
            highlightbackground=self.border,
            highlightthickness=1
        )
        result_card.pack(
            fill="both",
            expand=True
        )

        tk.Label(
            result_card,
            text="📋  CANDIDATE RANKING",
            bg=self.card,
            fg=self.text,
            font=("Segoe UI", 13, "bold")
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 10)
        )

        table_container = tk.Frame(
            result_card,
            bg=self.card
        )
        table_container.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 15)
        )

        columns = (
            "rank",
            "resume",
            "score",
            "similarity",
            "coverage"
        )

        self.tree = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings",
            height=9
        )

        self.tree.heading(
            "rank",
            text="Rank"
        )

        self.tree.heading(
            "resume",
            text="Candidate Resume"
        )

        self.tree.heading(
            "score",
            text="Match Score"
        )

        self.tree.heading(
            "similarity",
            text="Text Similarity"
        )

        self.tree.heading(
            "coverage",
            text="Keyword Coverage"
        )

        self.tree.column(
            "rank",
            width=70,
            anchor="center"
        )

        self.tree.column(
            "resume",
            width=330,
            anchor="w"
        )

        self.tree.column(
            "score",
            width=150,
            anchor="center"
        )

        self.tree.column(
            "similarity",
            width=160,
            anchor="center"
        )

        self.tree.column(
            "coverage",
            width=170,
            anchor="center"
        )

        scrollbar = ttk.Scrollbar(
            table_container,
            orient="vertical",
            command=self.tree.yview
        )

        self.tree.configure(
            yscrollcommand=scrollbar.set
        )

        self.tree.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.tree.bind(
            "<Double-1>",
            self.show_details
        )

        # =========================
        # STATUS BAR
        # =========================

        status_frame = tk.Frame(
            root,
            bg="#E2E8F0",
            height=30
        )
        status_frame.pack(
            fill="x",
            side="bottom"
        )
        status_frame.pack_propagate(False)

        self.status = tk.Label(
            status_frame,
            text="● Ready",
            bg="#E2E8F0",
            fg=self.muted,
            font=("Segoe UI", 9)
        )
        self.status.pack(
            side="left",
            padx=20
        )

    # =========================
    # STYLES
    # =========================

    def setup_styles(self):

        style = ttk.Style()

        try:
            style.theme_use("clam")
        except:
            pass

        style.configure(
            "Treeview",
            background="white",
            foreground=self.text,
            rowheight=38,
            fieldbackground="white",
            font=("Segoe UI", 10)
        )

        style.configure(
            "Treeview.Heading",
            background="#EFF6FF",
            foreground=self.text,
            font=("Segoe UI", 10, "bold"),
            padding=8
        )

        style.map(
            "Treeview",
            background=[
                ("selected", "#DBEAFE")
            ],
            foreground=[
                ("selected", self.text)
            ]
        )

    # =========================
    # SELECT JD
    # =========================

    def select_jd(self):

        path = filedialog.askopenfilename(
            title="Select Job Description",
            filetypes=[
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )

        if path:

            self.jd_path = path

            self.jd_label.config(
                text=os.path.basename(path),
                fg=self.text
            )

            self.status.config(
                text="● Job Description selected"
            )

    # =========================
    # SELECT RESUME FOLDER
    # =========================

    def select_resume_folder(self):

        folder = filedialog.askdirectory(
            title="Select Resume Folder"
        )

        if folder:

            self.resume_folder = folder

            self.resume_label.config(
                text=folder,
                fg=self.text
            )

            self.status.config(
                text="● Resume folder selected"
            )

    # =========================
    # SCREEN RESUMES
    # =========================

    def screen_resumes(self):

        if not self.jd_path:

            messagebox.showwarning(
                "Missing Job Description",
                "Please select the Job Description."
            )

            return

        if not self.resume_folder:

            messagebox.showwarning(
                "Missing Resumes",
                "Please select the resume folder."
            )

            return

        try:

            self.status.config(
                text="● Screening resumes..."
            )

            self.screen_button.config(
                state="disabled",
                text="⏳  SCREENING..."
            )

            self.root.update()

            results, keywords = resume_screener.score_resumes(
                self.jd_path,
                [self.resume_folder]
            )

            self.results = results
            self.keywords = keywords

            # Clear old table

            for item in self.tree.get_children():
                self.tree.delete(item)

            # Add results

            for rank, result in enumerate(
                results,
                start=1
            ):

                filename = os.path.basename(
                    result["file"]
                )

                score = result["score"] * 100
                similarity = result["similarity"] * 100
                coverage = result["coverage"] * 100

                self.tree.insert(
                    "",
                    "end",
                    values=(
                        rank,
                        filename,
                        f"{score:.2f}%",
                        f"{similarity:.2f}%",
                        f"{coverage:.2f}%"
                    )
                )

            # Top candidate

            if results:

                top = results[0]

                top_name = os.path.basename(
                    top["file"]
                )

                top_score = top["score"] * 100

                self.top_candidate.config(
                    text=
                    f"🏆  Top Candidate: "
                    f"{top_name}   |   "
                    f"Match Score: {top_score:.2f}%"
                )

            self.status.config(
                text=
                f"● Successfully screened "
                f"{len(results)} resumes"
            )

            messagebox.showinfo(
                "Screening Complete",
                f"{len(results)} resumes were successfully analyzed."
            )

        except Exception as e:

            messagebox.showerror(
                "Screening Error",
                str(e)
            )

            self.status.config(
                text="● Error occurred during screening"
            )

        finally:

            self.screen_button.config(
                state="normal",
                text="🔍  SCREEN RESUMES"
            )

    # =========================
    # SHOW DETAILS
    # =========================

    def show_details(self, event):

        selected = self.tree.selection()

        if not selected:
            return

        item = self.tree.item(
            selected[0]
        )

        rank = int(
            item["values"][0]
        )

        if rank <= 0 or rank > len(self.results):
            return

        result = self.results[rank - 1]

        filename = os.path.basename(
            result["file"]
        )

        score = result["score"] * 100
        similarity = result["similarity"] * 100
        coverage = result["coverage"] * 100

        details = tk.Toplevel(
            self.root
        )

        details.title(
            "Candidate Details"
        )

        details.geometry(
            "720x560"
        )

        details.configure(
            bg=self.bg
        )

        # Header

        header = tk.Frame(
            details,
            bg=self.primary,
            height=90
        )

        header.pack(
            fill="x"
        )

        header.pack_propagate(False)

        tk.Label(
            header,
            text="CANDIDATE DETAILS",
            bg=self.primary,
            fg="white",
            font=("Segoe UI", 18, "bold")
        ).pack(
            pady=25
        )

        # Candidate name

        tk.Label(
            details,
            text=filename,
            bg=self.bg,
            fg=self.text,
            font=("Segoe UI", 17, "bold")
        ).pack(
            pady=(20, 8)
        )

        # Score

        tk.Label(
            details,
            text=f"Overall Match Score: {score:.2f}%",
            bg=self.bg,
            fg=self.success,
            font=("Segoe UI", 14, "bold")
        ).pack(
            pady=5
        )

        tk.Label(
            details,
            text=f"Text Similarity: {similarity:.2f}%",
            bg=self.bg,
            fg=self.text,
            font=("Segoe UI", 11)
        ).pack()

        tk.Label(
            details,
            text=f"Keyword Coverage: {coverage:.2f}%",
            bg=self.bg,
            fg=self.text,
            font=("Segoe UI", 11)
        ).pack(
            pady=5
        )

        # Matched keywords

        matched_frame = tk.Frame(
            details,
            bg=self.card,
            highlightbackground=self.border,
            highlightthickness=1
        )

        matched_frame.pack(
            fill="x",
            padx=30,
            pady=(20, 8)
        )

        tk.Label(
            matched_frame,
            text="✓ Matched Keywords",
            bg=self.card,
            fg=self.success,
            font=("Segoe UI", 11, "bold")
        ).pack(
            anchor="w",
            padx=15,
            pady=(12, 5)
        )

        matched = ", ".join(
            result["matched_keywords"]
        )

        tk.Message(
            matched_frame,
            text=matched if matched else "None",
            width=620,
            bg=self.card,
            fg=self.text,
            font=("Segoe UI", 10)
        ).pack(
            anchor="w",
            padx=15,
            pady=(0, 12)
        )

        # Missing keywords

        missing_frame = tk.Frame(
            details,
            bg=self.card,
            highlightbackground=self.border,
            highlightthickness=1
        )

        missing_frame.pack(
            fill="x",
            padx=30,
            pady=8
        )

        tk.Label(
            missing_frame,
            text="✕ Missing Keywords",
            bg=self.card,
            fg="#DC2626",
            font=("Segoe UI", 11, "bold")
        ).pack(
            anchor="w",
            padx=15,
            pady=(12, 5)
        )

        missing = ", ".join(
            result["missing_keywords"]
        )

        tk.Message(
            missing_frame,
            text=missing if missing else "None",
            width=620,
            bg=self.card,
            fg=self.text,
            font=("Segoe UI", 10)
        ).pack(
            anchor="w",
            padx=15,
            pady=(0, 12)
        )

    # =========================
    # EXPORT CSV
    # =========================

    def export_csv(self):

        if not self.results:

            messagebox.showwarning(
                "No Results",
                "Please screen resumes first."
            )

            return

        path = filedialog.asksaveasfilename(
            title="Save Screening Results",
            defaultextension=".csv",
            filetypes=[
                ("CSV files", "*.csv")
            ]
        )

        if not path:
            return

        try:

            with open(
                path,
                "w",
                newline="",
                encoding="utf-8"
            ) as file:

                writer = csv.writer(file)

                writer.writerow([
                    "Rank",
                    "Resume",
                    "Match Score",
                    "Text Similarity",
                    "Keyword Coverage",
                    "Matched Keywords",
                    "Missing Keywords"
                ])

                for rank, result in enumerate(
                    self.results,
                    start=1
                ):

                    writer.writerow([
                        rank,
                        os.path.basename(
                            result["file"]
                        ),
                        f"{result['score'] * 100:.2f}%",
                        f"{result['similarity'] * 100:.2f}%",
                        f"{result['coverage'] * 100:.2f}%",
                        ", ".join(
                            result["matched_keywords"]
                        ),
                        ", ".join(
                            result["missing_keywords"]
                        )
                    ])

            messagebox.showinfo(
                "Export Successful",
                "Screening results exported successfully!"
            )

            self.status.config(
                text="● CSV exported successfully"
            )

        except Exception as e:

            messagebox.showerror(
                "Export Error",
                str(e)
            )

    # =========================
    # CLEAR
    # =========================

    def clear_results(self):

        for item in self.tree.get_children():
            self.tree.delete(item)

        self.results = []
        self.keywords = []

        self.top_candidate.config(
            text="🏆  Top Candidate: Not available"
        )

        self.status.config(
            text="● Results cleared"
        )


# =========================
# START APPLICATION
# =========================

if __name__ == "__main__":

    root = tk.Tk()

    app = ResumeScreenerGUI(root)

    root.mainloop()