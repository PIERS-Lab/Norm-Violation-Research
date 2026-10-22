import { useState } from 'react'
import './App.css'
import { useQuery } from '@tanstack/react-query'

const HOSTSERVER = "http://localhost:3000"
// Constructs the blocks for any sub-elements.
  function SubHeader({ text })
{
  return(
  <div className="block"> {text}</div>
  ) 
}
// display the image for the orders
// This is using data gotten from the server so there's an image, alt text, and the scores


async function get_data()
{
  const fetch_dat = await fetch(`${HOSTSERVER}/state`)
  // avoid using bad data if the HTTPS request doesn't work for whatever reason
  if (!fetch_dat.ok)
  {
    throw new Error(`HTTP Error, could not get the puzzle! ${fetch_dat.status}`);
  }

  return fetch_dat.json()
}

// main starting point for the app
function App() {
  const [count, setCount] = useState(1)
  let orderNum;
  orderNum = ("Order Number: " + count)
  const {data, isPending, error} = useQuery({
    queryKey: ['state'],
    queryFn: get_data,
    refetchInterval: 5000
  });
  
  if (isPending) {
    return <div>Loading...</div>;
  }

  else if (error) {
    return <div> Something went wrong :/ .</div>;
  }

  else {
  console.log("New data:", data);
  //setCount(count + 1)
  return <>
  { /* div is a formatless directive, use if you want to make a custom object */ }
  <div className='titleHead'>
        Big Delivery Co.
    </div> 
  <div style={{ display: 'flex', flexDirection: 'row' }}>
    {/* First Column */}
    <div className={'column'}>
      <div>
        <SubHeader text={orderNum} />
      </div>
      <div>
        <img className='order' src = {`${HOSTSERVER}${data.img_url}`}/>
      </div>
      
      { /* place the image under all the header info via load order */ }
      {/* for next session, have the response to server info be to edit the image and scores, then incerement the counter*/}
    </div>   
  
    {/* Second Column */}
    <div className={'column'}> 
      <div>
        <SubHeader text={"Team Credit"} />
      </div> 
      <div className='scoreBox'>
        <div> {`Human: ${data.body.humanScore}`} </div>
        <div> {`Left Robot: ${data.body.leftRobotScore}`} </div> 
        <div> {`Right Robot: ${data.body.rightRobotScore}`} </div>

      </div>
    
    </div>   
  </div>
  <div className='titleHead' style={{marginTop:'auto', display:'flex'}}></div>  
    {/* <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <div className='titleHead'>
        Credit
      </div>
       */}
  
  
  </>    
  }
}
// This makes the app fuction the starting point for the program
export default App
