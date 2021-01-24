let alarmTimeJs;
let standardTimeJs = 8;

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



window.onload = function(){

  YUI().use('dial', function(Y) {

    let dial = new Y.Dial({
      min:0,
      max:24,
      stepsPerRevolution:12,
      value: alarmTimeJs,
      label:'Wake me up at:', resetStr:'Reset', tooltipHandle:'Drag to set value'
    });
    
    dial.set('strings',{'label':'Wake me up at:', 'resetStr':'Reset', 'tooltipHandle':'Drag me!'});
    dial.render('#my-demo');


    // Function to update the text input value from the Dial value
    function updateInput( e ){
      var val = e.newVal;
      if ( isNaN( val ) ) {
        // Not a valid number.
        return;
      }
      this.set( "value", val );
    }

    var theInput = Y.one( "#myTextInput" );
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
}
