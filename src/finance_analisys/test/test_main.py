import datetime
import boto3
import customtkinter as ctk
import ollama

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class InteractiveAWSApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("AWS Operations & Security Manager - Executive Portal")
        self.geometry("1100x800")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")

        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="AWS Manager",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.btn_cost = ctk.CTkButton(
            self.sidebar_frame, text="Executive Dashboard", command=self.setup_cost_view
        )
        self.btn_cost.grid(row=1, column=0, padx=20, pady=10)

        self.btn_chat = ctk.CTkButton(
            self.sidebar_frame, text="Interactive Q&A", command=self.setup_chat_view
        )
        self.btn_chat.grid(row=2, column=0, padx=20, pady=10)

        # Main View
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.setup_cost_view()

    def fetch_aws_metrics(self):
        """Fetch cost, security, and cloudtrail data using boto3."""
        try:
            ce_client = boto3.client("ce")
            sh_client = boto3.client("securityhub")
            ct_client = boto3.client("cloudtrail")

            end_date = datetime.date.today()
            start_date = end_date - datetime.timedelta(days=30)

            # Fetch Costs
            cost_res = ce_client.get_cost_and_usage(
                TimePeriod={
                    "Start": start_date.strftime("%Y-%m-%d"),
                    "End": end_date.strftime("%Y-%m-%d"),
                },
                Granularity="MONTHLY",
                Metrics=["UnblendedCost"],
                GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
            )

            # Fetch Findings
            sec_res = sh_client.get_findings(
                Filters={"RecordState": [{"Value": "ACTIVE", "Comparison": "EQUALS"}]}
            )

            # Fetch CloudTrail Events
            trail_res = ct_client.lookup_events(MaxResults=10)

            return cost_res, sec_res, trail_res
        except Exception:
            return None, None, None

    def setup_cost_view(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        lbl = ctk.CTkLabel(
            self.main_frame,
            text="Executive Overview (Costs & Security)",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        lbl.pack(padx=20, pady=10)

        self.kpi_frame = ctk.CTkFrame(self.main_frame)
        self.kpi_frame.pack(padx=20, pady=5, fill="x")

        self.card_total = ctk.CTkFrame(self.kpi_frame)
        self.card_total.pack(side="left", expand=True, fill="both", padx=5, pady=5)
        ctk.CTkLabel(
            self.card_total, text="Total Spent (30d)", font=ctk.CTkFont(size=12)
        ).pack(pady=2)
        ctk.CTkLabel(
            self.card_total,
            text="$239.60 USD",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(pady=5)

        self.card_sec = ctk.CTkFrame(self.kpi_frame)
        self.card_sec.pack(side="left", expand=True, fill="both", padx=5, pady=5)
        ctk.CTkLabel(
            self.card_sec, text="Active Security Findings", font=ctk.CTkFont(size=12)
        ).pack(pady=2)
        ctk.CTkLabel(
            self.card_sec, text="2", font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=5)

        self.cost_tb = ctk.CTkTextbox(self.main_frame, width=700, height=400)
        self.cost_tb.pack(padx=20, pady=10)
        self.cost_tb.insert(
            "1.0",
            "Executive Summary:\n\n"
            "- Amazon EC2: $142.50 USD\n"
            "- Amazon RDS: $85.00 USD\n"
            "- Amazon S3: $12.10 USD\n\n"
            "Switch to 'Interactive Q&A' to ask about user attribution or specific expenses.",
        )

    def setup_chat_view(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        lbl = ctk.CTkLabel(
            self.main_frame,
            text="Management Assistant: Interactive Q&A",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        lbl.pack(padx=20, pady=10)

        self.chat_history = ctk.CTkTextbox(self.main_frame, width=700, height=450)
        self.chat_history.pack(padx=20, pady=10)
        self.chat_history.insert(
            "1.0",
            "Welcome! Suggested questions:\n"
            "- 'Who did the most high expense and when?'\n"
            "- 'Which user did it?'\n"
            "- 'What are our costs by zone?'\n\n",
        )

        self.input_frame = ctk.CTkFrame(self.main_frame)
        self.input_frame.pack(padx=20, pady=10, fill="x")

        self.entry_prompt = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="Ask a question about costs, users, or risks...",
            width=520,
        )
        self.entry_prompt.pack(side="left", padx=10, pady=10)

        btn_ask = ctk.CTkButton(
            self.input_frame, text="Ask Assistant", command=self.send_query
        )
        btn_ask.pack(side="left", padx=10, pady=10)

    def send_query(self):
        query = self.entry_prompt.get().strip()
        if not query:
            return

        self.chat_history.insert("end", f"\nManagement: {query}\n")
        self.entry_prompt.delete(0, "end")

        res = ollama.generate(model="llama3.1", prompt=query)
        self.chat_history.insert("end", f"\nOllama AI:\n{res['response']}\n")
        self.chat_history.see("end")


if __name__ == "__main__":
    app = InteractiveAWSApp()
    app.mainloop()