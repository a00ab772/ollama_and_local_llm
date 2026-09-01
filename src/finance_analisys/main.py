import datetime
import threading
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

        # Sidebar Frame
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

        # Main View Frame
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.setup_cost_view()

    def fetch_aws_metrics(self):
        """Fetch live cost, security, and cloudtrail data using boto3."""
        try:
            ce_client = boto3.client("ce")
            sh_client = boto3.client("securityhub")
            ct_client = boto3.client("cloudtrail")

            end_date = datetime.date.today()
            start_date = end_date - datetime.timedelta(days=30)

            cost_res = ce_client.get_cost_and_usage(
                TimePeriod={
                    "Start": start_date.strftime("%Y-%m-%d"),
                    "End": end_date.strftime("%Y-%m-%d"),
                },
                Granularity="MONTHLY",
                Metrics=["UnblendedCost"],
                GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
            )

            sec_res = sh_client.get_findings(
                Filters={"RecordState": [{"Value": "ACTIVE", "Comparison": "EQUALS"}]}
            )

            trail_res = ct_client.lookup_events(MaxResults=10)

            return cost_res, sec_res, trail_res
        except Exception as e:
            return None, None, str(e)

    def setup_cost_view(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        lbl = ctk.CTkLabel(
            self.main_frame,
            text="Executive Overview (Costs & Security)",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        lbl.pack(padx=20, pady=10, anchor="w", fill="x")

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

        self.cost_tb = ctk.CTkTextbox(self.main_frame, height=500)
        self.cost_tb.pack(padx=20, pady=10, fill="both", expand=True)
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
        lbl.pack(padx=20, pady=10, anchor="w", fill="x")

        self.chat_history = ctk.CTkTextbox(self.main_frame)
        self.chat_history.pack(padx=20, pady=10, fill="both", expand=True)
        self.chat_history.insert(
            "1.0",
            "Welcome! Ask any live question regarding costs, users, or infrastructure.\n\n",
        )

        self.input_frame = ctk.CTkFrame(self.main_frame)
        self.input_frame.pack(padx=20, pady=10, fill="x")

        self.entry_prompt = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="Ask a question about costs, users, or risks...",
        )
        self.entry_prompt.pack(side="left", fill="x", expand=True, padx=10, pady=10)

        self.btn_ask = ctk.CTkButton(
            self.input_frame, text="Ask Assistant", command=self.send_query
        )
        self.btn_ask.pack(side="right", padx=10, pady=10)

    def send_query(self):
        query = self.entry_prompt.get().strip()
        if not query:
            return

        self.chat_history.insert("end", f"\nManagement: {query}\n")
        self.chat_history.insert("end", "\nOllama AI: Thinking...\n")
        self.chat_history.see("end")
        self.entry_prompt.delete(0, "end")
        self.btn_ask.configure(state="disabled")

        # Run Ollama call asynchronously so the UI does not freeze
        threading.Thread(target=self._get_ollama_response, args=(query,), daemon=True).start()

    def _get_ollama_response(self, query):
        cost_data, sec_data, trail_data = self.fetch_aws_metrics()

        system_context = (
            "You are an AWS Cloud Cost & Infrastructure Management AI Assistant.\n"
            "Use the provided AWS Telemetry Data to accurately answer the user's question.\n"
            "If exact data is missing from the metrics, provide standard AWS operational advice.\n\n"
            f"AWS Telemetry Data:\n"
            f"- Cost Data: {cost_data}\n"
            f"- Security Findings: {sec_data}\n"
            f"- CloudTrail Logs: {trail_data}\n\n"
            f"User Question: {query}"
        )

        try:
            res = ollama.generate(model="llama3.1", prompt=system_context)
            response_text = res["response"]
        except Exception as err:
            response_text = f"Error connecting to Ollama: {str(err)}"

        self.after(0, self._update_chat_ui, response_text)

    def _update_chat_ui(self, response_text):
        # Remove 'Thinking...' placeholder line and append live response
        self.chat_history.delete("end - 2 lines", "end")
        self.chat_history.insert("end", f"\nOllama AI:\n{response_text}\n\n")
        self.chat_history.see("end")
        self.btn_ask.configure(state="normal")


if __name__ == "__main__":
    app = InteractiveAWSApp()
    app.mainloop()