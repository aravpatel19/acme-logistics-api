# Video Walkthrough Script - Acme Logistics Demo
## Duration: 5 minutes

---

### Opening (0:00-0:30)

"Carlos, I know you requested an automated solution for handling inbound carrier calls, and I've built exactly what Acme Logistics needs. 

Right now, your team spends 70% of their time on basic carrier verification and load matching. We're going to change that today.

Let me show you the system that's already live and processing carrier calls 24/7."

---

### Use Case Setup (0:30-1:30)

"Here's the business problem we're solving:

When carriers call Acme looking for loads, your agents have to:
- First, verify their MC number with FMCSA - that's 3-5 minutes per call
- Search through available loads 
- Negotiate rates within your margins
- Only then can they actually close the deal

Our AI agent handles all of that automatically. Let me show you the workflow."

[Screen: HappyRobot Platform - Agent Configuration]

"The agent is configured with your business rules:
- It verifies every carrier through FMCSA in real-time
- Searches loads based on their location and equipment
- Negotiates within the 5% margin you've set
- And only transfers qualified, price-agreed carriers to your team"

[Screen: Show the workflow nodes]

"Notice how we built in your exact business logic - the same questions your best agents ask, in the right order."

---

### Live Demo (1:30-3:30)

"Let's see it in action. I'll call in as a carrier."

[Action: Initiate web call to the agent]

**Demo Call Flow:**
- "Hi, I'm calling about available loads. My MC number is 999999"
- Show FMCSA verification happening in real-time
- "I'm in Chicago with a dry van"
- Show load matching based on location
- Brief negotiation showing the AI handling a counteroffer
- Transfer to sales team

[Screen: Show API logs during the call]

"See how the API instantly verified the carrier, found matching loads, and handled the negotiation - all in under 2 minutes. Your agent would have spent 10 minutes on this same call."

---

### Dashboard Analytics (3:30-4:30)

[Screen: Live Dashboard]

"Now here's where it gets powerful - your real-time command center.

Look at these metrics:
- We're showing a 37% booking rate on verified carriers
- Average negotiation takes just 1.8 rounds
- Each booked load averaging $4,500 in revenue

[Point to different dashboard sections]

"You can see exactly which carriers called, what they were looking for, and why they booked or didn't book. This visibility helps you optimize your load pricing and identify patterns.

Notice the sentiment analysis - you'll know if carriers are frustrated with rates before it becomes a relationship issue.

And this updates every 10 seconds - your managers have their finger on the pulse of carrier activity."

---

### Business Impact & Closing (4:30-5:00)

"Let's talk ROI:

With 100 carrier calls per day, you're saving 500 minutes of agent time daily. That's over 8 hours - a full employee's day.

But more importantly, you're capturing the 40% of calls that come in after hours. That's pure incremental revenue you're missing today.

The system is live right now at this URL [show URL]. Your team can start using it immediately.

This isn't about replacing your agents - it's about letting them do what they do best: building relationships and closing deals. The AI handles the repetitive work, your team handles the revenue.

Questions?"

---

## Key Presentation Notes:

1. **Energy**: Start strong, maintain confidence throughout
2. **Focus**: Business value over technical details
3. **Proof**: Show real results, not promises
4. **Urgency**: They're losing money every day without this

## Technical Elements to Have Ready:

1. Browser tab with HappyRobot platform logged in
2. Browser tab with live dashboard 
3. Phone/computer ready for web call demo
4. API documentation page (only if asked)

## Anticipated Questions:

**Q: "What if the system makes a mistake?"**
A: "Every interaction is logged. Your team can review and adjust. Plus, the AI only operates within the parameters you set - it can't agree to rates outside your margins."

**Q: "How hard is this to maintain?"**
A: "It's completely managed. You just update your load inventory as you normally would. The AI training and infrastructure are handled for you."

**Q: "What about our existing phone system?"**
A: "This runs in parallel. You can start with 10% of calls and scale up as you see results. No disruption to current operations."