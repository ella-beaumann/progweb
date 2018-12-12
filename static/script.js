console.log("toto")

/* FONCTIONS DE TEST */
function activateButton() {
  document.getElementById("submitbutton").disabled=false;
  console.log(document.getElementById("submitbutton"))
}

function ecouteBouton(){
  document.getElementById("submitbutton")
  .addEventListener("mouseover", function(){
    console.log("mouse over submit button")
  })
}

/* VRAIES FONCTIONS DU TP */

function validateForm(){
  let checking_form = validateRequiredData()
  console.log(checking_form)
  if (checking_form === true){
    document.getElementById("submitbutton").disabled=false;
  }
}

function validateRequiredData(){
  // required_data=["Ensembl_Gene_ID","Chromosome_Name","Gene_Start","Gene_End"]
  let add_gene_form = document.getElementsByClassName("form_val")
  let checking_form = true
  for (let form of add_gene_form){
    form.addEventListener("input", function(e){
      let name = e.target.name;
      let input_value = e.target.value
      if (name === "gene_id"){
        if (input_value === "" || input_value === " "){
          msg = "Please enter a valid Ensembl gene ID."
          document.getElementById("gene_id_error").innerHTML = msg;
          document.getElementsByName(name)[0].style.borderBottom = "2px solid red";
          checking_form = false;
        } else {
          document.getElementsByName(name)[0].style.borderBottom = "2px solid green";
          document.getElementById("gene_id_error").innerHTML = "";
        }
      }
      if (name === "chr_name"){
        if (input_value === "" || input_value === " "){
          msg = "Please enter a valid chromosome name."
          document.getElementById("chr_error").innerHTML = msg;
          document.getElementsByName(name)[0].style.borderBottom = "2px solid red";
          checking_form = false;
        } else {
          document.getElementsByName(name)[0].style.borderBottom = "2px solid green";
          document.getElementById("chr_error").innerHTML = "";
        }
      }
      if (name === "gene_start"){
        if (input_value === "" || input_value === " " || input_value === "0" || Number.isNaN(Number(input_value))){
          msg = "Gene start must be a number greater or equal to 1."
          document.getElementById("gene_start_error").innerHTML = msg;
          document.getElementsByName(name)[0].style.borderBottom = "2px solid red";
          checking_form = false;
        } else {
          document.getElementsByName(name)[0].style.borderBottom = "2px solid green";
          document.getElementById("gene_start_error").innerHTML = "";
        }
      }
      if (name === "gene_end"){
        if (input_value === "" || input_value === " " || input_value === "0" || Number.isNaN(Number(input_value))){
          msg = "Gene end must be a number."
          document.getElementById("gene_end_error").innerHTML = msg;
          document.getElementsByName(name)[0].style.borderBottom = "2px solid red";
          checking_form = false;
        } else {
          let gene_start = document.getElementsByName("gene_start")[0].value
          if (input_value <= gene_start){
            msg = "Gene end must be greater than gene start."
            document.getElementById("gene_end_error").innerHTML = msg;
            document.getElementsByName(name)[0].style.borderBottom = "2px solid red";
            checking_form = false;
          } else {
            document.getElementsByName(name)[0].style.borderBottom = "2px solid green";
            document.getElementById("gene_end_error").innerHTML = "";
          }
        }
      }
      if (name === "a_gene_name"){
        if (input_value === "" || input_value === " " ){
          // no input, doesnt matter
          //document.getElementsByName(name)[0].style.borderBottom = "2px solid red";
        } else {
          document.getElementsByName(name)[0].style.borderBottom = "2px solid green";
        }
      }
      if (name === "band"){
        if (input_value === "" || input_value === " " ){
          // no input, doesnt matter
          //document.getElementsByName(name)[0].style.borderBottom = "2px solid red";
        } else {
          document.getElementsByName(name)[0].style.borderBottom = "2px solid green";
        }
      }
      if (name === "strand"){
        //let selected_strand = Number(document.getElementsByName(name)[0].value
        //if (input_value === "" || input_value === " " ){
          // no input, doesnt matter
          //document.getElementsByName(name)[0].style.borderBottom = "2px solid red";
        //} else {
          //document.getElementsByName(name)[0].style.borderBottom = "2px solid green";
        //}
      }
      if (name === "transcript_count"){
        if (input_value === "" || input_value === " " ){
          // no input, doesnt matter
          //document.getElementsByName(name)[0].style.borderBottom = "2px solid red";
        } else {
          document.getElementsByName(name)[0].style.borderBottom = "2px solid green";
        }
      }
    })
  }
  return checking_form;
}

validateForm();
