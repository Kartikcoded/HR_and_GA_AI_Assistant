from app.agent.graph import agent

r1 = agent.invoke({"question": "How many casual leave days do I get per year?"})
print("Case 1 (knowledge gap → ticket):", r1.get("answer"))

r2 = agent.invoke({"question": "My laptop screen is cracked, I need a replacement"})
print("Case 2 (direct action):", r2.get("answer"))

r3 = agent.invoke({"question": "What time does the office open?"})
print("Case 3 (should be answerable):", r3.get("answer"))