var fukidashi2, mmd, koro;
enchant();

var MOTION_PATH = {
  boredom  : 'motion/mei_idle_boredom.vmd',
  think    : 'motion/mei_idle_think.vmd',
  yawn     : 'motion/mei_idle_yawn.vmd',
  laugh    : 'motion/mei_laugh.vmd',
  breath   : 'motion/mei_breath.vmd',
  left     : 'motion/mei_imagine_left_normal.vmd',
  right    : 'motion/mei_imagine_right_normal.vmd',
  greeting : 'motion/sd_mei_greeting.vmd'
};

// Speech Synthesis
var msg = new SpeechSynthesisUtterance();
msg.volume = 1.0;
msg.rate = 1.0;
msg.pitch = 1.0;
msg.lang = "ja-JP";
msg.voice = speechSynthesis.getVoices().filter(function(voice) { return voice.name == "Google 日本人"; })[0];

function submit_message(){
  koro = mmd.getModelRenderer("korokoro");
  document.getElementById("info").innerText = "へんじをかんがえてます...";

  var think = new MMD.Motion(MOTION_PATH['think']);
  think.load(function() {
    think.loop = true;
    koro.addModelMotion("think", think);
    koro.play("think");
  });

  users_input = document.getElementById("text").value;
  console.log(users_input);
  httpObj = new XMLHttpRequest();
  function speech(httpObj){
    if ((httpObj.readyState == 4) && (httpObj.status == 200)){
      console.log(httpObj.responseText);

      fukidashi2 = create_fukidashi(httpObj.responseText, 100, 700, 'yellow');
      game.rootScene.addChild(fukidashi2);

      msg.text = httpObj.responseText;
      window.speechSynthesis.speak(msg);

      document.getElementById("info").innerText = "もっとはなそう！";
      var yawn = new MMD.Motion(MOTION_PATH['yawn']);
      yawn.load(function() {
        yawn.loop = true;
        koro.addModelMotion("yawn", yawn);
        koro.play("yawn");
      });
    } else{
      var laugh = new MMD.Motion(MOTION_PATH['laugh']);
      laugh.load(function() {
        laugh.loop = true;
        koro.addModelMotion("laugh", laugh);
        koro.play("laugh");
      });
    }
  }
  httpObj.onreadystatechange = function(){speech(httpObj);};
  if (httpObj){
    url = 'http://mamisan.no-ip.org/api/dialogue/?text='+users_input;
    httpObj.open("GET", url, true);
    httpObj.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    httpObj.send();
  }
  document.getElementById("text").value = "";
  document.getElementById("text").focus();
}

function think(){
  if (document.getElementById("text").value.length == 1){
    koro = mmd.getModelRenderer("korokoro");
    var think = new MMD.Motion(MOTION_PATH['think']);
    think.load(function() {
      think.loop = true;
      koro.addModelMotion("think", think);
      koro.play("think");
    });
  }
}

window.onload = function() {
  document.getElementById("text").focus();
  game = new Game(1000, 1000);
  game.onload = function() {
    var scene = new Scene3D();
  var camera = scene.getCamera();
  camera.y = 20;
  camera.z = 80;
  camera.centerY = 10;

    var canvas = document.getElementsByTagName('canvas')[0];
    mmd = new MMD(canvas, canvas.width, canvas.height);
    mmd.registerKeyListener(canvas);
    mmd.registerMouseListener(canvas);

    mmd.addModel("korokoro", new MMD.Model('model/korokoro', 'korokoro.pmd'));

    mmd.load(function() {
      var koro = mmd.getModelRenderer("korokoro");
      koro.translate(0, 6, 0.0);

      var greet = new MMD.Motion(MOTION_PATH['greeting']);
      greet.load(function() {
        greet.loop = false;
        koro.addModelMotion("greeting", greet);
        koro.play("greeting");
      });

      mmd.start();
      mmd.play();
    });
    game.rootScene.addChild(mmd);

    var oldX = 0;
    r = Math.PI / 2;

    game.rootScene.addEventListener('touchstart', function(e) {
        oldX = e.x;
    });
    game.rootScene.addEventListener('touchmove', function(e) {
      r += (e.x - oldX) / 100;
      camera.x = Math.cos(r) * 80;
      camera.z = Math.sin(r) * 80;
      oldX = e.x;
    });

    var label = new Label('0');
    label.font = '24px helvetica';
    label.color = '#fff';
    game.rootScene.addChild(label);
    var c = 0;
    setInterval(function() {
      label.text = c;
      c = 0;
    }, 1000);
    game.rootScene.addEventListener('enterframe', function(e) {
        c++;
    });
  };
  game.start(); //ゲーム開始
};
