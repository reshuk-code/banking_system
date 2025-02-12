/*
 * This code belongs to reshuk-code.
 * Contact: business.reshuksapkota@gmail.com
 * Git-Hub: https://github.com/reshuk-code
 * 
 * This program is open source and built for a personal project.
 * You are free to use, modify, and distribute this code for non-commercial purposes.
 * However, commercial use of this code is strictly prohibited.
 * 
 * © 2025 Reshuk Sapkota. All rights reserved.
 */



import express from 'express';
const app = express()
app.get('/' , (req , res)=>{
    res.send('Things are under development')
})
app.listen(3000 , ()=>{
    console.log('Server is running on port 3000')
})
