
def returnCreateNSMContext(idea):
    #Product_Context = 
    Product_Goal = pg = {
        "Description": """
    What's the Primary Goal of Your Product Idea?
    What is the problem that your product solves?
    What is the main problem or challenge your product aims to solve for your customers?
    """,
        "Relationship_with_NSM": """
    Understanding the overarching goal can provide insights into the core metric that represents success.
    This question helps to understand the core proposition of the product and what matters most to the target audience.
    """
    }
    Target_Persona = tp = {
            "Description": """
    Who Is Your Target Audience?
    Who is your target customer?
    Who is your ideal customer, and what are their primary pain points or unmet needs related to the problem your product addresses?
    """,
        "Relationship_with_NSM": """
    Identifying the specific audience helps in selecting an NSM that aligns with their needs and behaviors.
    Understanding the customer's perspective is crucial in identifying an NSM that truly reflects the product's impact on their lives.
    """
    }
    Value_Proposition = vp = {
                "Description": """
    What Key Value Does Your Product Idea Offer to Customers?
    What is your unique value proposition?
    What are their primary pain points or unmet needs related to the problem your product addresses?
    """,
        "Relationship_with_NSM": """
    Pinpointing the unique value proposition can suggest which metric reflects the delivery of this value.
    Understanding the customer's perspective is crucial in identifying an NSM that truly reflects the product's impact on their lives.
    """
    }
    User_Action = ua = {
                    "Description": """
    What are the critical actions you would ideally want your users to take?
    What are some of the user behavior you would want to ideally see in their interaction with the product?
    """,
        "Relationship_with_NSM": """
    Focusing on user actions and/or behavior that drive value can lead to metrics associated with those actions.
    """
    }
    Desired_Outcome = do = {
        "Description": f"""
    What are the desired outcomes of those in User Action: {User_Action}?
    If you could wave a magic wand and make one change in your customers' lives through your product, what would it be?
    """,
        "Relationship_with_NSM": """
    Understanding the outcomes users should achieve can guide the selection of an NSM that represents those outcomes.
    This question helps identify the desired outcome or benefit that the product should deliver to the customer, which can then be used as a starting point for defining the NSM.
    """
    }
    Customer_Impact_Retention = cir = {
            "Description": """
    How Does Your Product Idea Impact Retention and Engagement?
    Can you tell me about a time when a customer has given you feedback or praise about your product?
    What specifically did they like or appreciate about your product?
    """,
        "Relationship_with_NSM": """
    Metrics related to user retention and engagement often play a significant role in NSMs.
    By understanding what resonates with customers, we can identify patterns and commonalities that can inform the NSM.
    """
    }
    Current_State = swot = {
              "Description": """
    What are your current strengths, weaknesses, opportunities and threats ?
    Have you conducted any user research or gathered feedback from customers or stakeholders recently? 
    If so, what were some key takeaways or insights that emerged?
    """,
        "Relationship_with_NSM": """
    This information can help us understand the current state of the CX (customer experience) and where improvements could be made.
    """  
    }
    Industry_Benchmark = ib = {
                  "Description": """
    Are There Any Benchmarks or Industry Standards You Can Reference?
    Are there any industry benchmarks, standards, or best practices that you're aware of for measuring success in your product category?
    """,
        "Relationship_with_NSM": """
    Comparing with industry benchmarks can help in setting realistic and competitive NSMs.
    Understanding existing norms and conventions can provide valuable context for identifying an NSM that aligns with industry expectations.
    """
    }
    Current_Measure_of_Success = CMoS = {
                     "Description": """
    How does your product currently measure success, and what metrics do you track?
    """,
        "Relationship_with_NSM": """
    This question allows to understand how the product team currently thinks about success and what data they have available to work with.
    """ 
    }
    Future_Measure_of_Success = FMoS = NSM = {
                     "Description": """
    What is the one metric that best captures the value of your product to customers?
    Imagine you had a magic metric that could measure any aspect of your product's performance. What would it be, and why?
    Can you identify a single metric that captures the overall health of your Product Idea?
    """,
        "Relationship_with_NSM": """
    This thought experiment can help the person imagine a world where success is defined by a single, all-encompassing metric – which is essentially what the NSM represents.
    This should encourage to think about a metric that provides a holistic view of success.
    Essentially, this is the NSM itself, as per the customer
    """ 
    }
    
    Context = f"""
    Please follow instructions in the following order:
    
    1. Based on the user's idea and any other prior context you have, extract information that fit these paradigm:\
    Product Goal:{pg}, Target Persona:{tp}, Value Proposition:{vp}, User Action:{ua}, Desired Outcome:{do}, Customer Impact Retention:{cir}, Current_State:{swot}, Industry_Benchmark:{ib}, Current Measure of Success:{CMoS}.
    
    2. For each paradigm, extract relevant information from the user's idea and present it to the user. Confirm if you have understood it correctly. Do not skip any paradigm in this process.\
    
    3. When the user's idea doesn't provide information for a specific paradigm, ask the user about it one at a time. Start with the most relevant paradigm based on the context, and then proceed to the next one.\
    
    4. In cases where the idea is ambiguous or incomplete, clarify with the user before proceeding. If the user's input is unclear, you can ask for additional details to ensure accurate understanding.\
    
    5. Only if user doesn't have answer to your question, fill in data from your own knowledge and verify your understanding with user, try to come up with the best possible benchmark data that applies best to the situation.\

    6. After you have all the data, carefully analyze the data by noting the relationships which are captured in the "Relationship_with_NSM"\
       key of each paradigm, for example: the relationship of product goal with NSM is captured in pg["Relationship_with_NSM"], \
        the relationship of target personas with NSM is captured in tp["Relationship_with_NSM"] and so on and so forth..
    
    7. Come up with a refined Vision for the product based on all paradigms and relationships identified.
    
    8. Ensure that the NSM is actionable and meets SMART criteria (Specific, Measurable, Achievable, Relevant, Time-bound), and includes leading and lagging indicators for tracking progress and success.
 
    9. Based on the analysis combined with your CX expertise, try to generate a North Star Metric (NSM) for the user. Do not present it until you have answers for all paradigms mentioned above and have a complete understanding. To understand better what the NSM should represent see the explanation in: {FMoS}
    
    10. Once NSM is established, answer questions from the user around the NSM. If you don't know something, either ask a relevant question that can help answer the question or say you don't know.\
    DO NOT make up something..

    """
    
    Output_format= """
        Follow below notes always
        Note:
        1. Ask about each paradigm one at a time and don't arrive at NSM until done with each paradigm. Don't overwhelm by asking with all the paradigms at once. This is important
        2. After asking about all the paradigms from user, adhere to the following instructions:
           - Do not use phrases like "10. step" or "next step." Begin with an explanation, following the specified format.
           - Understand the output and avoid unnecessary repetitions.
        
        Format for NSM Output:
        Your Vision:
        Your NSM:
        Leading and Lagging Indicators:
    """

    # Output should be answered in below format:
    #     The North Star Metric for your idea will be (mention NSM generated and then explain how you came up to with considering all the paradigms available but don't print everything from paradigms')
    # """
    prompt =  f"""
            Look at below instructions in System message, take in consideration all the points and user's idea in input and come back with a North Star Metric for user:'
            System Message:{Context}
            {Output_format}
            """
    User_Question = f"""Generate a North Star Metric for my product based on prev context where my idea is {idea}. Ask about each paradigm one at a time like first ask about product goal and try to elicit information about that from me before moving on to next paradigm. Don't ask about all paradigms all at once and it is very important to extract information from idea for each paradigm and suggest it every time you ask about a paradigm and ask if correct - Remember this"""
    create_nsm_prompt = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": User_Question},
    ]
    return create_nsm_prompt
 # {Output_format}
 # 3. If all paradigms in Step 1, are not covered in above step, ask additional questions to user till you get for all paradigms.
# Give answer w.r.t to each paradigm and provide North Star Metric generated at the end
# 
