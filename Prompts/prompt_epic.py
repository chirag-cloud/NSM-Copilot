def return_epic_prompt(NSM,idea,prevConvo):
    context =  f"""
                1. The North Star Metric (NSM) for this scenario is '{NSM}', determined by an NSM Copilot who collected data from users with various perspectives and paradigms.
                2. Take into consideration the most recent conversation between the user and the Copilot: '{prevConvo}', which may include user interviews.
                3. The central idea or vision is '{idea}'.
                Generate a minimum of 10 Epics in the CX/UX category based on the NSM.
                """
    Output_format = """Generate epics in below format:
                        Here are your epics:
                        1. (Heading of Epic): (Describe the epic)
                        2..... and so on
                     """
    prompt = f"""Look at below instructions in System message, take in consideration all the points and user's NSM in input and come back with generating Epics for it:'
                System message: {context}
                {Output_format}"""
    
    return prompt

