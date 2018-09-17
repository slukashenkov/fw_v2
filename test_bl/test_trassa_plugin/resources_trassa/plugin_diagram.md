```puml
@startuml
participant AIS_TRASSA 
participant KD  
participant ASTD 


autonumber 01
group exchange_1
    AIS_TRASSA ->KD: PCMST(A/V)
    KD ->ASTD: ASTD Bin MSG
end

autonumber stop
group exchange_2
KD -> AIS_TRASSA: PEIST(A/V)\nnevery 1 sec
end
autonumber 01
group exchange_3
    AIS_TRASSA ->KD: AIALR/AITXT 
    KD -->ASTD: AIALR/AITXT\n as is
end
autonumber stop
autonumber 01
group exchange_4
    AIS_TRASSA ->KD: AIVDM\n(Type 1,5,18,24) 
    KD -->AIS_TRASSA: PAIDD/PAISD
end
autonumber stop
@enduml
```

