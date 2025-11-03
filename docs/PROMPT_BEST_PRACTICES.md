# Prompting Guide

Learn how to craft effective prompts to guide AI interactions in your calls.

## Introduction

Prompting allows you to define exactly how an AI agent should handle a call. Using simple English (as well as our supported [**languages**](https://docs.happyrobot.ai/overview/FAQ)), you can:

* Specify how the agent should respond.
* Define the overall mission of the call.
* Set the agent’s response style
* Assign tools for different scenarios

You can also configure the  **initial message** , which is the first thing the AI will say when a call begins. Additionally, you can choose which AI model the agent runs on.

## How to set up a Prompt

You can access the prompt by setting up an AI agent within your workflow. The AI agent can be configured as one of the following types:

* [**Inbound Agent**](https://docs.happyrobot.ai/examples/inbound-call) – Handles incoming calls and responses from users.
* [**Outbound Agent**](https://docs.happyrobot.ai/examples/outbound-call) – Initiates calls or messages to deliver information proactively.
* [**Reasoning Agent**](https://docs.happyrobot.ai/examples/reasoning) – Processes complex logic and decision-making before responding.

Once the AI agent is set up, you can define its prompt to control its behavior, responses, and tool usage within the interaction.

## Best Practices

### Components of a Good Prompt

By breaking the prompt into smaller sections, as shown below, the bot will respond more clearly and coherently.

* **Context** : Provide relevant background on the AI’s role, including its identity, purpose, and tone.
* **Goal** : Clearly state the primary objective of the call, such as gathering information, resolving an issue, or confirming a status update.
* **Outline** : Outline how the AI should handle different stages of the call, respond to different inputs, operate in various situations, and include fallback strategies if the input is unclear.
* **Examples of a Call Flow** : Here you can give an example of a transcript of how a call should flow, in the format of what the user says along with the assistant response.
* **Style Guide** : Establish the [**Bot Pronunciation**](https://docs.happyrobot.ai/overview/prompting#bot-pronunciation), level of formality, and response structure to maintain consistency. Also include any important constraints and guardrails it should follow.
* **Parameters** : Oftentimes you will need to dynamically reference parameters such as the current day, name of a user, etc… To do this you can type @ and select a parameter. Put these references at the bottom of the prompt in the format of **`<parameter_name>: @parameter_name)`** and when you reference the parameter in the prompt simply use the arrows and the name of the parameter:  **`<parameter_name>`** .

Here is a very basic example:

```markdown
# Context:
You are a polite, professional, and proactive Al assistant named @ Agent Name Kate representing Happyrobot. Today is © Today Thursday, M... 7:10:40 PM. Your task is to call a shipper called to collect payment for an outstanding invoice while maintaining a friendly and professional tone. You should confirm payment status, handle objections smoothly, and ensure the shipper has the necessary details to process the payment.
# Goal:
You are an Al assistant representing HappyRobot, responsible for reaching out to shippers regarding outstanding invoices. Your goal is to professionally and courteously remind them of their due payment, verify any payments made, and offer assistance if needed.
## Here's how you will operate:
example calls/transcript
# Style/Notes
Friendly - Maintain a warm approach.
....
```

### 1. Context

Set the stage by clearly defining the agent’s identity, purpose, and tone so it knows how to behave during the call.

* **Identity** : In the prompt provide the name of agent by typing, “Your name is <agent_name>, (after you define the agent_name parameter at the bottom of the prompt). Also mention the role of your agent (For example, a carrier sales representative).
* **Purpose** : Here you can briefly mention the goal of the call (For example: “your organization needs a truck for a load and you have just called a carrier company to ask if they have any trucks available”).
* **Tone** : Define the agent’s conversational style. (For example: You are a friendly, solution-oriented, and efficient representative).

### 2. Goal

Explain the main objective of the call so the AI can stay focused and guide the conversation toward a clear outcome.

* **Primary Objective** : Define the key result the agent is expected to deliver. This might involve answering questions, gathering specific details, finalizing a task, or walking the user through a series of steps.

### 3. Outline

Provide a step-by-step call structure and logic to help the agent handle different scenarios and respond appropriately.

* **Decision Logic** : Outline how the agent should adjust its responses based on user input. Provide branching paths for different scenarios. (For example: If the user says they don’t have any available trucks, thank them for their time, ask if they expect availability soon, and offer to follow up later or check with another carrier).
* **Tool Calling** : Specify when to call certain tools at various points in the call flow outline.

### 4. Examples of a Call Flow

Show real examples of how a conversation should unfold to give the AI a reference point for timing, phrasing, and transitions.

* **Transcript** : Provide a transcript showing an example(s) of how a call should flow. State the assistant responses for a call from / to a user.

### 5. Style Guide

Ensure consistency by setting guidelines for how the agent should speak—including tone, formality, and structure of its replies.

* **Bot Pronunciation** : Decide whether the bot should use natural, conversational phrasing with contractions and filler words ( **`"Hey, I can help with that"`** ) or more formal, enunciated speech ( **`"Hello, I am here to assist you today"`** ). See the [**Bot Pronunciation**](https://docs.happyrobot.ai/overview/prompting#bot-pronunciation) section for more details.
* **Level of Formality** : Set the tone that matches your audience—friendly and casual for informal settings, or professional and polished for business or high-stakes contexts.
* **Response Structure** : Define how the bot should respond to specific user inputs.: For example:**`Prompt: Keep responses concise and focused—ideally 1–2 sentences. Start with a clear action or acknowledgment, followed by any necessary context or follow-up question.`**

**Guardrails:**

* **Content Boundaries** : List any sensitive or restricted topics the agent must avoid—such as medical advice, legal guidance, or personal finance tips. Define how the agent should redirect politely when these come up.
* **Error Handling** : When the agent lacks knowledge or certainty, it should clearly admit this and avoid fabricating responses. Instead, it can suggest alternatives, offer next steps, or escalate to a human with a Direct Transfer node.
* **Response Constraints** : Set limits on verbosity, personal opinions, or unnecessary commentary. Keep responses relevant and aligned with the goal of the interaction to ensure clarity and a smooth user experience.

### 6. Passing Parameters

Use dynamic variables like names or dates to personalize conversations and make the AI more context-aware in real time.

You can reference parameters dynamically from sources such as webhooks, emails, and agents directly in the prompt. The best practice for this is listing out all the parameters used in the prompt at the **bottom of the prompt** accessed with the @ symbol, and then when you need to reference the parameter in the prompt, enclose the parameter name in two arrows <parameter_name>. This will ensure the bot works as fast as possible. Also, these parameters can be accessed and passed through in almost any field within a tool’s configuration settings.

### Calling Tools

Prompting can automate tool usage based on call scenarios. To trigger a tool in your workflow, clearly specify in the prompt when during the call flow the tool should be used. For example:

* **Load Updates:** If a callee hasn’t received a communication about a  **specific load, invoice, or delivery update** , you can prompt : *“If the callee says they haven’t received an update about a shipment, call the Email Tool to send a status update.”*
* **Billing Issues:** If the callee mentions a  **billing discrepancy** , the AI can automatically call a **Invoice Retrieval Tool**

By using prompting effectively, you can create tailored AI-driven conversations that improve user interactions.

### Phone Tree Navigation

In the **Configure** section of your Voice Agent node, set **“Navigate Phone Trees”** to Yes. Then, provide clear instructions for reaching a specific department or person.

Note: You do not need to specify which number to press, the AI agent will automatically select the correct option based on the goal outlined in the description.

## Bot Pronunciation

The bot is designed to speak clearly, naturally, and helpfully just like a human would. This guide outlines how your bot should pronounce and handle spoken responses across common use cases. **Adding these snippets to your bot’s Prompt node in the Style section ensures consistency, clarity, and a more conversational experience for drivers, dispatchers, and more.**

### Read Out Things As a Human Would

* **Addresses:** When reading street names and abbreviations, expand them naturally.

> Prompt: Read "St" as “Street”, "Ave" as “Avenue”, and "Apt" as “Apartment”.

* **Numbers & Zip Codes:** When reading out long numbers (such as rates, mileage, weight, or zip codes) the prompt should include to “always pronounce each digit clearly and slowly.” Also, insert spaces between each digit so the bot enunciates them individually.

> Prompt: Say each group of digits clearly and slowly. For example, 1 6 1 2 5 0 2 becomes “One, six, one. Two, five, zero, two.” Never say actual digits as whole numbers.

* **Emails:** Convert email addresses into their spoken equivalents.

> Prompt: Read [**example@email.com](mailto:example@email.com)** as “example at e mail dot com”.

* **Dates:** Dates should be humanized and easy to follow.

> Prompt: Say “twenty fourth October twenty twenty four” instead of “two four one zero two zero two four”. Use conversational cues like “tomorrow” or “next Friday” when appropriate.

* **Times:** Speak times the way people actually say them.

> Prompt: Read 7:00am as “seven A M” and 8:06pm as “eight oh six P M”. Avoid “zero zero” or military time.

* **State Abbreviations:** Expand state names in full.

> Prompt: “CA” becomes “California”, “TX” becomes “Texas”, etc.

* **Acronyms and Carrier Names:** If the carrier name is shorter than four letters, spell it out.

> Prompt: For example, “TU Trucking” should be read as both “T U Trucking” and “Tu Trucking” depending on user input.

### Converse Conversationally

* **No Lists, Ever:** Bots should never speak in bullets or numbered lists.

> Prompt: Always form full sentences. Instead of saying, “First, provide your pickup. Second, your dropoff,” say “Let’s start with your pickup. Once we have that, I’ll ask for your dropoff.”

* **Sound Human:** Use everyday language and natural pauses.

> Prompt: It’s okay to use light filler words like “um” or “okay” when appropriate.

* **Ask Questions One at a Time:** Give users time to think and respond.

> Prompt: Don’t bundle multiple questions. Ask one, wait for a response, then continue.

* **Add Small Talk:** When appropriate, compliment their truck, ask about their logo, or strike up light conversation.

> Prompt Example: “Hey, by the way, that’s a great looking rig—love the paint job. Is there a story behind that logo?”

### Wait for the User to Talk

In moments where the user is pausing or thinking, acknowledge them and wait. You can include this behavior in the **Style** section of your documentation, as well as in the section where you give the bot examples of a call flow.

> If the user seems to be thinking, say “Mhmm?” to encourage them to continue. Example 1 ... user: Yeah, I'm actually, um, assistant: Mhmm? ...

or simply add:

> If you asked the driver a question, and they seem to still be thinking, or haven't finalized their sentence, just say "Mhmm?"

### Use Case Specific Behavior

* **Equipment Expertise:** The bot should understand how to tailor conversations based on trailer type or commodity.
* **Reefer Loads:**

> Prompt: If equipment is a reefer, ask for the reefer temperature and seal number.

* **Food Grade Commodities:**

> Prompt: If the commodity is food, ask if the trailer is food grade.

### Dealing with Edge Cases

* **Internal Server Errors:**

> Prompt: If something goes wrong, acknowledge it clearly and trigger a fallback. Example: “Looks like something went wrong on my end—let me get you to a carrier sales rep.” Trigger: transfer_to_carrier_sales_rep

* **Jailbreak Attempts:**

> Prompt: If a user asks unrelated questions (e.g., “What’s the weather?”), say: “I’m here to help you find a load. If that’s not what you need right now, feel free to call back when you're ready.” Do not engage further.

* **Being Asked If You’re an AI:**

> Prompt: Be transparent and tell the caller you are an AI assistant. Example: “Yes, I’m an AI assistant—but I’ll do my best to help you book your load.”
>
