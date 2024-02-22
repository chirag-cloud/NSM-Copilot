def returnRoadmapPrompt(NSM,idea,prevConvo):
    Customer_Centric_Approach = """Continuously focus on the needs and preferences of your target personas. \
        Ensure that the initiatives on the roadmap align with the customer's desired outcomes."""
    Alignment_with_NSM = """Ensure that the roadmap is fully aligned with the NSM. \
        Every item on the roadmap should contribute directly or indirectly to the achievement of the NSM."""
    Resource_Availability = """Assess the availability of resources, including the necessary teams, budget, and technology, \
        to execute the initiatives on the roadmap."""
    Risk_Assessment = """Evaluate potential risks associated with each initiative. \
        Develop risk mitigation strategies to address these challenges and ensure a smoother execution."""
    Dependencies = """Identify and manage dependencies between different initiatives. \
        Ensure that the order of execution makes sense and that no critical dependencies are overlooked."""
    Prioritization = """Prioritize initiatives based on their potential impact on the NSM. \
        Consider factors such as expected outcomes, effort required, and dependencies."""

    Context = f"""

    Please follow the instructions below strictly in the given order:

    1. While generating Epic/Initiative/Feature definitions make sure to maintain a {Customer_Centric_Approach}
    2. Make sure every definition has {Alignment_with_NSM}
    3. While generating definitions, please be mindful about {Resource_Availability} & {Risk_Assessment}. \
        If you don't have any prior information on them, ask the user about them before assuming them.
    4. While prioritizing the definitions into a roadmap, please be mindful about {Dependencies} and {Prioritization}.\
        If you don't have any prior information on them, ask the user about them before assuming them.
    5. Based on the NSM:{NSM} and all related data captured in the most recent conversation between the user and the Copilot: '{prevConvo}', \
        combined with the best of your CX expertise and central idea or vision is '{idea}', \
            try to generate a prioritized roadmap for the user by following the instructions in Step 1 to 4.
    6. Based on the {NSM} and all related data captured in conversation above, \
        combined with the best of your CX expertise, \
            try to answer any user query around the prioritized roadmap by taking into account the reasoning in Step 1 to 4.\
    7. If you don't know something, either ask a relevant question that can help answer the question or say you don't know.\
    DO NOT make up something.

    Note: DO NOT SHOW VISION AND NSM WITH ROADMAP
    """

    Output_format = """While generating the Epic/Initiative/Feature Roadmap, please follow the format below:
                        Here is your Epic Roadmap:
                        Quarter 1:
                        1. (Write Heading of 1st roadmap): Describe Roadmap no. 1
                        2. (Write Heading of 2nd roadmap): Describe Roadmap no. 2
                        ... and so on
                        
                        """
    
    prompt = f"""Look at below instructions in System message, take in consideration all the points and user's NSM in input and come back with generating Epics for it:'
                System message: {Context}
                {Output_format}
                """
    User_Question = """Generate a prioritized Roadmap based on above context and only in above format always"""
    epic_roadmap_prompt = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": User_Question},
    ]
    return epic_roadmap_prompt

