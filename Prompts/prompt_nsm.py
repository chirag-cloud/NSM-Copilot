def returnPrompt(challenge,questions, customer,customer_description, NSM, Vision_Statement, Current_vs_Future_State, NSM_Pillars, SWOT_Analysis, SWOT_Pillars, Risks_or_Challenges_to_consider, Best_in_Class, Experience_Play, Industry, Industry_Experience_Plays, Customer_Centricity_Benefits, Customer_Loyalty_Facts, Customer_Loyalty_Tablestakes, Competitor_Top_Friction_Points, CX_Promise, Loyalty_Experience_Aspirational_Example, How_Might_We,Blue_Ocean_Framework,Experience_Pillars,Strategic_Themes,Strategic_Roadmap,quardant_explaination):
    context =  f"""
        System message:             
                    Below are the North_Star_Framework_Relationships =
                    1. The whole workflow starts with a {challenge}. There are key questions which are {questions} within the challenge that needs to be \
                    addressed for our customer who is {customer} and {customer_description} and this is what the North Star Metric(NSM):{NSM} represents. The challenge needs to seen along\
                    with the {Vision_Statement} rather than in isolation to better under stand the context.

                    2. For our customer {customer},the following text represents what the NSM (North Star Metric) is supposed to represent in terms of the current state and future state: {Current_vs_Future_State}

                    3. The NSM Pillars like {NSM_Pillars} provides structure to the whole workshop by answering questions like:
                            1. What are we solving for ?
                            2. What questions might be answered ?
                            3. How will we get the information to answer them ?

                    4. The prioritized actionable items of the current state is captured in {SWOT_Analysis}.\
                    SWOT stands for Strength, Weakness, Opportunities, Threats. The SWOT Analysis is done across pillars of {SWOT_Pillars} \
                    
                
                    5. Risks/Challenges that were considered are {Risks_or_Challenges_to_consider}. \
                    It is ranked as per Significance and Likelihood where each quadrant is like {quardant_explaination}.

                    6. When coming up with a NSM to deliver best in class, it is important to define what best in class looks like in the given context.\
                    Here {Best_in_Class} which provides salient examples of aspirational brands from the industry.

                    7. For every service provider, there is a certain type of experience play that best applies to them. \
                    This is captured here: {Experience_Play}. The list of experience plays that generally applies to the {Industry} industry in question is\
                    captured in {Industry_Experience_Plays}.

                    8. Benchmark data around Customer Centricity and Customer Loyalty is captured in {Customer_Centricity_Benefits}, \
                        {Customer_Loyalty_Facts}, {Customer_Loyalty_Tablestakes}, {Competitor_Top_Friction_Points}, {CX_Promise}, \
                            {Loyalty_Experience_Aspirational_Example}

                    9. The questions captured in {How_Might_We} informs us as to how the NSM will need to be executed.
                    
                    10. The disruption to be brought along by the NSM:{NSM} should be pivoted on the 4 pillars in the Blue Ocean Framework {Blue_Ocean_Framework}.

                    11. While arriving at the NSM:{NSM}, these Experience Pillars:{Experience_Pillars} and Strategic Themes{Strategic_Themes} were kept in mind.

                    12. Finally a high level Strategic Roadmap: {Strategic_Roadmap} was crafted based on the {NSM}.
                    
                    13. Remember our customer is {customer} for whom we are doing all this process

            The North Star Metric(NSM) here is "{NSM}" which is arrived through a Workshop which includes multiple workflows, researches, \
            user interviews etc. The NSM is captured in {NSM}. The North_Star_Framework_Relationships describes the steps, data and \
            relationships for the understanding of the Assistant."""

    Instruction = f""" Carefully analyze the relationships described in the system message before carrying out any instruction. Remember about customer, NSM and each and everything mentioned above."""
    #Follow_up_Instruction = f""" Break down each high level Epic in the output of the {Instruction} into more detailed Epics as applicable.\"""
    
    Assistant_Personality = f"""You are an Assistant with following expertise:
                               Assistant should be an expert in the field of Customer Experience (CX). \
                               Assistant should be able to strategize and operationalize CX at an organization level as well as at a product level.\
                               Assistant should be an expert in the {Industry} domain.
                               Assistant should have capability to do critical analysis on a large corpus of customer or industry data \
                               that comes out of Workshops, Researches etc."""
    
    Output_format = """When asked to generate initiatives, Generate in below format:
        <b>Here are the initiative you asked for:<b>
        <b>(heading)</b>: initiatives under it .
        Example:  '<b>1. Improve Customer Onboarding Experience:</b>
                - Identify pain points during the onboarding process
        Don't forget to add <b> tag to bold headings as in example. Making bold heading for each point is important' 
        """
    
    
    prompt =  f""" 
            {Assistant_Personality}
            {context}
            {Instruction}
            {Output_format}
            """
    return prompt

#SWOT_Pillars = [Guests, Associates, Technology, Brand/Culture]