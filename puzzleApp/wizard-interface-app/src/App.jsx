import { useState } from 'react'
import './App.css'
import FileInput from './components/FileInput'
import Button from './components/Button'
import SubmitBox from './components/submitBox'
const HOSTSERVER = "http://10.116.28.103:3000/state"
//const HOSTSERVER = "http://0.0.0.0:3000/state"

function App() {
  const [puzzle, setPuzzle] = useState(null)
  const [hscore, setHScore] = useState(0)
  const [r1score, setR1Score] = useState(0)
  const [r2score, setR2Score] = useState(0)
  // async function updateData()
  // {
  //   console.log("button press!");
  //   const formData = new FormData();
  //   // Package everything into a format that can be sent to a server 
  //   formData.append('puzzle', puzzle);
  //   formData.append('hscore', 10);
  //   formData.append('r1score', 20);
  //   formData.append('r2score', 30);
  //   const response = await fetch(HOSTSERVER, {
  //   method:"POST",
  //   body: formData
  //   })
  //   console.log("Server response:", response.status)
  //   console.log(await response.text())
  // };
  async function updateData()
{
  console.log("button press!");

  const formData = new FormData();

  formData.append("puzzle", puzzle);
  formData.append("humanScore", hscore);
  formData.append("leftRobotScore", r1score);
  formData.append("rightRobotScore", r2score);

  console.log("Sending:", puzzle);

  try {
    const response = await fetch(HOSTSERVER, {
      method: "POST",
      body: formData
    });

    console.log("Response:", response.status);
    console.log(await response.text());

  } catch (error) {
    console.error("Fetch error:", error);
  }
}
  
  
  // const [count, setCount] = useState(0)
  return <>
  <FileInput onFileSelect = {setPuzzle}/>
  <SubmitBox labeltext = "Human score" setvalue = {setHScore} />
  <SubmitBox labeltext = "Left robot score" setvalue = {setR1Score} defaultvalue = "0"/> 
  <SubmitBox labeltext = "Right robot score" setvalue = {setR2Score} defaultvalue = "0"/>  
  <button onClick={updateData}>update display</button> 

  </> 

}

export default App






















// export default App



// import { useState } from 'react'
// import './App.css'
// import base from '../../Puzzles/base_puzzle.png'

// // Constructs the blocks for any sub-elements.
//   function SubHeader({ text })
// {
//   return(
//   <div className="block"> {text}</div>
//   ) 
// }
// // display the image for the orders
// function order({ image, text })
// {
//   return <img src = {image} alt = {text} height={800} width={400}/> 
// }

// // main starting point for the app
// function App() {
//   const [count, setCount] = useState(1)
//   let name, orderNum;
//   name = "Bill"
//   orderNum = ("Order Number: " + count) 
//   return <>
//   // div is a formatless directive, use if you want to make a custom object
//   <div className= 'titleHead'>
//     Big Delivery Co.
//   </div> 
//   // flex forces the entire object to print on one line, both headers would be stacked vertically otherwise.
//   <div style={{display:'flex'}}>
//     <SubHeader text = {name}/> 
//     <SubHeader text = {orderNum}/>
//   </div>
//   // place the image under all the header info via load order
//   <div>
//     <img src = {base} alt = "Base puzzle" height={800} width={600} />
//   </div>

//   </>

// }
// // This makes the app fuction the starting point for the program
// export default App
