const express = require('express');
const mysql = require('mysql');
const bodyParser = require('body-parser');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
require("dotenv").config();
const articles = require('./articles.json');

const DB_HOST = process.env.DB_HOST
const DB_USER = process.env.DB_USER
const DB_DATABASE = process.env.DB_DATABASE
const DB_PASSWORD = process.env.DB_PASSWORD

const db = mysql.createConnection({
  host: DB_HOST,
  user: DB_USER,
  database: DB_DATABASE,
  password: DB_PASSWORD,
});

db.connect((err) => {
  if (err) {
    throw err;
  }
  console.log('Connected to MySQL server');
});

const app = express();
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());
const jwtSecret = 'patypet_secret';
const globalInfo = {};


app.post('/register', async (req, res) => {
  const { name, email, password } = req.body;
  globalInfo.email = email;
  globalInfo.name = name;
  
  if (!emailRegex.test(email)) {
    res.status(400).json({ error: 'Invalid email format' });
    return;
  }

  try {
    const hashedPassword = await bcrypt.hash(password, 10);
    
    const sql = 'INSERT INTO users (name, email, password) VALUES (?, ?, ?)';
    db.query(sql, [name, email, hashedPassword], (err, result) => {
      if (err) {
        res.status(500).json({ error: 'Failed to register user' });
      } else {
        res.status(200).json({ message: 'User registered successfully' });
      }
    });
  } catch (error) {
    res.status(500).json({ error: 'Failed to register user' });
  }
});

app.post('/login', (req, res) => {
  const { email, password } = req.body;
  const sql = 'SELECT * FROM users WHERE email = ?';
  const { email: globalEmail, name: globalName } = globalInfo;
  db.query(sql, [email], async (err, result) => {
    if (err) {
      res.status(500).json({ error: 'Failed to log in' });
    } else if (result.length === 0) {
      res.status(401).json({ error: 'Invalid credentials' });
    } else {
      const match = await bcrypt.compare(password, result[0].password);
      if (match) {
        const token = jwt.sign({ email: result[0].email, name: result[0].name }, jwtSecret, {
          expiresIn: '1h'
        });
        
        res.status(200).json({ name: result[0].name, token: token });
      } else {
        res.status(401).json({ error: 'Invalid credentials' });
      }
    }
  });
});

app.get('/user', (req, res) => {
  const token = req.headers.authorization;
  const { email: globalEmail, name: globalName } = globalInfo;
  if (!token) {
    res.status(401).json({ error: 'Authorization token not provided' });
  } else {
    jwt.verify(token, jwtSecret, (err, decoded) => {
      if (err) {
        res.status(401).json({ error: 'Invalid token' });
      } else {
        const { email, name } = decoded;
        const sql = 'SELECT id, name, email FROM users WHERE email = ?';
        db.query(sql, [email], (err, result) => {
          if (err) {
            res.status(500).json({ error: 'Failed to fetch user information' });
          } else if (result.length === 0) {
            res.status(404).json({ error: 'User not found' });
          } else {
            const user = result[0];
            res.status(200).json({ id: user.id, name: user.name, email: user.email });
          }
        });
      }
    });
  }
});

app.get('/articles', (req, res) => {
  const { jenis } = req.query;
  let filteredArticles = articles;
  
  if (jenis) {
    filteredArticles = articles.filter(article => article.jenis === jenis);
  }
  
  res.json(filteredArticles);
});

app.get('/getGlobalInfo', (req, res) => {
  res.json(globalInfo);
});

app.listen(3000, () => {
  console.log('Server started on port 3000');
});
