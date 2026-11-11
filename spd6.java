const requireAdmin = (
  req,
  res,
  next
) => {
  if (req.user.role !== "admin") {
    return res.status(403).json({
      message: "Forbidden"
    });
  }

  next();
};

module.exports = requireAdmin;
const router = require("express").Router();

const authenticate =
  require("../middlewares/authenticate");

const requireAdmin =
  require("../middlewares/require_admin");

router.use(authenticate);
router.use(requireAdmin);

router.get("/dashboard", (req, res) => {
  res.json({
    message: "Dashboard data"
  });
});

router.get("/categories", (req, res) => {
  res.json({
    message: "Categories"
  });
});

router.get("/foods", (req, res) => {
  res.json({
    message: "Foods"
  });
});

router.get("/orders", (req, res) => {
  res.json({
    message: "Orders"
  });
});

module.exports = router;
const express = require("express");

const app = express();

app.use(express.json());

app.use(
  "/admin",
  require("./routes/admin.routes")
);

module.exports = app;
const app = require("./app");

app.listen(5000, () => {
  console.log("Server running");
});