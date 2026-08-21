const express = require("express");
const cors = require("cors");

const app = express();

app.use(cors());
app.use(express.json());

app.get("/", (req, res) => {
  res.json({
    project: "AI Based Startup Idea Validator",
    status: "Backend is running"
  });
});

app.get("/api/health", (req, res) => {
  res.json({
    status: "healthy"
  });
});

const PORT = process.env.PORT || 5000;

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});