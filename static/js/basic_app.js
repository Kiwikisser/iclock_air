let alarmTimeJs;
let standardTimeJs = 8;
let alarmTimeJs2;

function setVars(vars) {
  if (vars == undefined) {
    alarmTimeJs = standardTimeJs
    console.log("Set alarm time to: " + alarmTimeJs);
    return standardTimeJs
  } else {
    alarmTimeJs = vars
    console.log("Set alarm time to: " + alarmTimeJs);
    return vars
  }
}

function setVars2(vars) {
  if (vars == undefined) {
    alarmTimeJs2 = standardTimeJs
    console.log("Set alarm time to: " + alarmTimeJs2);
    return standardTimeJs
  } else {
    alarmTimeJs2 = vars
    console.log("Set alarm time to: " + alarmTimeJs2);
    return vars
  }
}



window.onload = function(){

  YUI().use('dial', function(Y) {

    let dial = new Y.Dial({
      min:0,
      max:23,
      stepsPerRevolution:12,
      value: alarmTimeJs,
      diameter: 200
      // label:'Wake me up at:', resetStr:'Reset', tooltipHandle:'Drag to set value'
    });

    dial.set('strings',{'label':'Wake me up at:', 'resetStr':'Cancel', 'tooltipHandle':'Drag me!'});
    dial.render('#my-demo');


    // Function to update the text input value from the Dial value
    function updateInput( e ){
      let val = e.newVal;
      if ( isNaN( val ) ) {
        // Not a valid number.
        return;
      }
      this.set( "value", val );
    }

    let theInput = Y.one( "#myTextInput" );
    // Subscribe to the Dial's valueChange event, passing the input as the 'this'
    dial.on( "valueChange", updateInput, theInput );

    // Function to pass input value back to the Slider
    function updateDial( e ){
      dial.set( "value" , e.target.get( "value" ) - 0);
    }
    theInput.on( "keyup", updateDial );

    // Initialize the input
    theInput.set('value', dial.get('value'));
  });

  YUI().use('dial', function(Y) {

    let dial2 = new Y.Dial({
      min:0,
      max:59,
      stepsPerRevolution:59,
      value: alarmTimeJs2,
      diameter: 180
      // label:'Wake me up at:', resetStr:'Reset', tooltipHandle:'Drag to set value'
    });

    dial2.set('strings',{'label':'Wake me up at:', 'resetStr':'Cancel', 'tooltipHandle':'Drag me!'});
    dial2.render('#my-demo2');


    // Function to update the text input value from the Dial value
    function updateInput( e ){
      let val = e.newVal;
      if ( isNaN( val ) ) {
        // Not a valid number.
        return;
      }
      this.set( "value", val );
    }

    let theInput = Y.one( "#myTextInput2" );
    // Subscribe to the Dial's valueChange event, passing the input as the 'this'
    dial2.on( "valueChange", updateInput, theInput );

    // Function to pass input value back to the Slider
    function updateDial2( e ){
      dial2.set( "value" , e.target.get( "value" ) - 0);
    }
    theInput.on( "keyup", updateDial2 );

    // Initialize the input
    theInput.set('value', dial2.get('value'));
  });
}
