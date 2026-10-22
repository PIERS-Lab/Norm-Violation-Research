import { useState } from "react";

// note, this component is expenting integration with a state variable
// A modular submit box, give it a lable, the set function for the variable of concern and a starting vlaue if desired
export default function SubmitBox({labeltext, setvalue, defaultvalue = 0})
{
    function handleSubmit(e)
    {
        e.preventDefault();
        const form = e.target;
        const formData = new FormData(form);
        const json = Object.fromEntries(formData.entries());
        console.log(json);
        setvalue(Number(json.inputField));    
    }

    return(
        <form method="post" onSubmit={handleSubmit}>
            <label>
                {labeltext} <input name = "inputField" defaultValue={defaultvalue}/>
            </label>
        </form>
    );
}    