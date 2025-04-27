import asyncio
import logging
import threading
import time
import gradio as gr
from app.agent.manus import Manus
from app.logger import logger

progress_data = {
    "status": "idle",
    "progress": 0,
    "details": []  # To store detailed execution steps
}

# Function to update progress details
def update_progress(status, progress, detail):
    global progress_data
    progress_data["status"] = status
    progress_data["progress"] = progress
    progress_data["details"].append(detail)

# Function to capture logs and update the progress UI
def capture_logs_to_ui():
    # Update UILogHandler to filter out logs from get_progress_ui
    class UILogHandler(logging.Handler):
        def emit(self, record):
            # Skip logs from get_progress_ui
            if "get_progress_ui" in record.name:
                return
            # Only include step-related logs
            if "step" in record.msg.lower():
                log_entry = self.format(record)
                update_progress("log", 0, log_entry)

    handler = UILogHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)

# Update the logger configuration to filter out logs from get_progress_ui
logging.getLogger("__main__.get_progress_ui").setLevel(logging.WARNING)

# Call this function at the start of the application
capture_logs_to_ui()

# Function to handle user input and process it with the Manus agent
def process_prompt(prompt):
    if not prompt.strip():
        logger.warning("Empty prompt provided.")
        return {"status": "error", "message": "Prompt cannot be empty."}

    try:
        # Update progress to processing
        update_progress("processing", 0, "Received prompt and starting processing.")

        logger.warning("Processing your request...")
        agent = Manus()
        asyncio.run(agent.run(prompt))

        # Update progress to completed
        update_progress("completed", 100, "Request processing completed.")

        logger.info("Request processing completed.")
        return {"status": "success", "message": "Request processed successfully."}
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return {"status": "error", "message": str(e)}

# Gradio interface
def reset_progress_ui():
    global progress_data
    progress_data = {
        "status": "idle",
        "progress": 0,
        "details": []
    }
    return "Progress reset successfully."

# Add debugging to confirm the data being passed to the Gradio UI
# Update the get_progress_ui function to log the progress_data
def get_progress_ui():
    logger.info(f"Progress data being sent to UI: {progress_data}")
    return progress_data  # Ensure all fields, including 'details', are returned

def start_progress_updater():
    def update_loop():
        while True:
            time.sleep(1)  # Update every second
            progress_data_to_ui = get_progress_ui()
            logger.info(f"Updating UI with progress data: {progress_data_to_ui}")
            progress_display.update(value=progress_data_to_ui)

    thread = threading.Thread(target=update_loop, daemon=True)
    thread.start()

# Update the Gradio interface to show detailed logs
with gr.Blocks() as ui:
    gr.Markdown("# Manus Agent Interface")

    with gr.Row():
        with gr.Column():
            prompt_input = gr.Textbox(label="Enter your prompt", placeholder="Type something...")
            submit_button = gr.Button("Submit")
            reset_button = gr.Button("Reset Progress")

        with gr.Column():
            progress_output = gr.JSON(label="Progress Details")  # Display full progress_data

    submit_button.click(process_prompt, inputs=prompt_input, outputs=progress_output)
    reset_button.click(reset_progress_ui, outputs=progress_output)

    gr.Markdown("---")
    gr.Markdown("Progress Status:")
    progress_display = gr.JSON(value=get_progress_ui())  # Show detailed logs in real-time

# Start the progress updater thread
start_progress_updater()

if __name__ == "__main__":
    ui.launch(server_name="0.0.0.0", server_port=5000)
