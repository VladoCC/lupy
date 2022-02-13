function test(a, b, c, d) 
    
    for i = 0, 3 do
        if i % 2 == 0 then
            print(i)
        end
    end
end

function test2() 
    for i = 1, 9 do
        if i % 2 == 0 then
            print(i)
        end
    end
end

function test3() 
    for i = 1, (45 % 5 - 1) do
        if i % 2 == 0 then
            print(i)
        end
    end
end

function foo(a) 
    print(a)
    b = 3 * a
    return a + 2
end

function bar(a) 
    if a % 3 == 1 then print(a)
    else  print(0)
    end
end

function bar2(a) 
    if not a(a) then print(a)
    else  print(0)
    end
end

function bar3(a) 
    if true then print(a)
    else  print(0)
    end
end

function bar4(a) 
    if not a then print(a)
    else  print(0)
    end
end

function bar5(a) 
    if a ~= a then print(a)
    else  print(0)
    end
end

function bar6(a) 
    if a and a then print(a)
    else  print(0)
    end
end

function bar7(a) 
    if a <= 5 then print(a)
    else  print(0)
    end
end

function another() 
    for i in pairs({[0] = 1, [1] = 2, [2] = 3}) do
        print(i)
    end
end

print("hello" + "world")
e = #(test(1, 2, 3, 4))
a = {test=1, t=2}
b = {[0] = 1, [1] = 2}
c = {[0] = 1, [test(a, a, a, a)] = 2}